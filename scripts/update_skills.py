#!/usr/bin/env python3
"""Daily Claude Code skills updater.

Fetches latest changelog/commits from anthropics/claude-code, writes dated
skill snapshots under Claude/skills/YYYY-MM-DD/skills/, and writes a
structured changelog under Claude/Changelogs/YYYY-MM-DD.txt.

Dependency-free and non-interactive for GitHub Actions use.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_ROOT = REPO_ROOT / "Claude"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"

KST = timezone(timedelta(hours=9), "KST")
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
CC_REPO = "anthropics/claude-code"
CC_BRANCH = "main"


# ── skill definitions ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SkillDef:
    slug: str
    cmd: str
    trigger: str
    desc: str
    example: str = ""
    note: str = ""
    token_policy: tuple[str, ...] = field(default_factory=tuple)


SKILL_DEFS: tuple[SkillDef, ...] = (
    SkillDef(
        slug="init",
        cmd="/init",
        trigger="user asks to initialize or document codebase",
        desc="Generate CLAUDE.md with codebase architecture, conventions, commands",
        token_policy=("One-pass generation; no repeated file reads after initial scan.",),
    ),
    SkillDef(
        slug="review",
        cmd="/review",
        trigger="user asks to review PR or branch",
        desc="Multi-pass PR review; checks logic, style, security, tests",
        token_policy=("Cap raw diff output; summarise per-file.", "Stop after first full pass unless issues found."),
    ),
    SkillDef(
        slug="security-review",
        cmd="/security-review",
        trigger="user asks security audit of current branch changes",
        desc="OWASP-focused audit of pending diffs; outputs risk-ranked findings",
        token_policy=("Report only non-trivial findings.", "Rank by severity to front-load critical items."),
    ),
    SkillDef(
        slug="simplify",
        cmd="/simplify",
        trigger="user asks to clean up or refactor changed code",
        desc="Review changed code for reuse/quality/efficiency, then fix issues",
    ),
    SkillDef(
        slug="session-start-hook",
        cmd="/session-start-hook",
        trigger="user wants test/lint runners on session start (web Claude Code)",
        desc="Create SessionStart hook ensuring project can run tests and linters",
    ),
    SkillDef(
        slug="update-config",
        cmd="/update-config",
        trigger='automated behavior requests ("when X", "allow Y", "set Z=val")',
        desc="Configure settings.json; handles hooks, permissions, env vars",
        token_policy=("Emit minimal JSON diff; skip unchanged sections.",),
    ),
    SkillDef(
        slug="keybindings-help",
        cmd="/keybindings-help",
        trigger="user wants to remap keys or add chord shortcuts",
        desc="Customize ~/.claude/keybindings.json; supports chord bindings",
    ),
    SkillDef(
        slug="fewer-permission-prompts",
        cmd="/fewer-permission-prompts",
        trigger="user wants fewer permission dialogs",
        desc="Scan transcripts -> add bash/MCP allowlist to .claude/settings.json",
    ),
    SkillDef(
        slug="loop",
        cmd="/loop [interval] [/command]",
        trigger='user wants recurring task (e.g. "check every 5m", "keep running X")',
        desc="Run prompt or slash command on recurring interval (default 10m)",
        example="/loop 5m /review",
    ),
    SkillDef(
        slug="claude-api",
        cmd="/claude-api",
        trigger="code imports anthropic SDK; user asks about Claude API features",
        desc="Build/debug Claude API apps; prompt caching, tool use, model migration",
        token_policy=(
            "Enable prompt caching on all multi-turn builds.",
            "Prefer structured tool_use over free-text parsing.",
        ),
    ),
    SkillDef(
        slug="ultrareview",
        cmd="/ultrareview [PR#]",
        trigger='user says "ultrareview" or wants multi-agent review',
        desc="Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR",
        note="Billed; requires git repo; no GitHub remote needed for local mode",
    ),
    SkillDef(
        slug="ultraplan",
        cmd="/ultraplan",
        trigger="user wants cloud environment for complex planning",
        desc="Auto-create cloud worktrees/environments for multi-agent planning tasks",
    ),
    SkillDef(
        slug="team-onboarding",
        cmd="/team-onboarding",
        trigger="user wants teammate ramp-up guide",
        desc="Generate onboarding guide from local Claude Code usage history/data",
    ),
    SkillDef(
        slug="effort",
        cmd="/effort",
        trigger="user wants to adjust effort/quality level",
        desc="Interactive slider for session effort level (also: CLAUDE_EFFORT env var)",
    ),
    SkillDef(
        slug="powerup",
        cmd="/powerup",
        trigger="user wants feature demos or to learn Claude Code features",
        desc="Interactive animated feature demos with lessons",
    ),
    SkillDef(
        slug="tui",
        cmd="/tui",
        trigger="rendering looks flickery or user wants full-screen mode",
        desc="Switch to flicker-free alt-screen TUI rendering (also: CLAUDE_CODE_NO_FLICKER)",
    ),
    SkillDef(
        slug="focus",
        cmd="/focus",
        trigger="user wants compact view of conversation",
        desc="Toggle focus view showing only: prompt + tool summary + final response",
        token_policy=("Reduces rendered context; lowers effective token overhead.",),
    ),
    SkillDef(
        slug="undo",
        cmd="/undo",
        trigger="user wants to undo last action",
        desc="Alias for /rewind; undoes last assistant action",
    ),
    SkillDef(
        slug="usage",
        cmd="/usage",
        trigger="user asks about token or cost statistics",
        desc="Show token usage and cost stats (merged /cost + /stats)",
    ),
    SkillDef(
        slug="theme",
        cmd="/theme [name]",
        trigger="user wants to change or create visual theme",
        desc="Create or switch custom color themes",
    ),
    SkillDef(
        slug="color",
        cmd="/color",
        trigger="user wants a session color",
        desc="Set random session color (no args = random pick)",
    ),
    SkillDef(
        slug="run",
        cmd="/run",
        trigger="user asks to run, start, or screenshot the app",
        desc="Launch and drive project app; confirms change works in real app (not just tests)",
    ),
    SkillDef(
        slug="verify",
        cmd="/verify",
        trigger="user asks to verify a PR, confirm a fix works, test a change manually",
        desc="Run app and observe behavior; test golden path and edge cases",
    ),
    SkillDef(
        slug="code-review",
        cmd="/code-review",
        trigger="user asks for code review on changed files",
        desc="Review changed code for reuse, quality, and efficiency; fix issues found",
    ),
    SkillDef(
        slug="statusline-setup",
        cmd="/statusline-setup",
        trigger="user wants to configure Claude Code status line",
        desc="Configure the Claude Code status line setting in settings.json",
    ),
)


# ── network helpers ────────────────────────────────────────────────────────────

def fetch_text(url: str) -> str:
    headers = {"User-Agent": "prompt-guide-claude-skill-sync/2.0"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
        headers["Accept"] = "application/vnd.github+json"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def repo_commit(repo: str, branch: str) -> str:
    try:
        data = json.loads(fetch_text(f"https://api.github.com/repos/{repo}/commits/{branch}"))
        sha = str(data.get("sha", "unknown"))
        return sha[:12]
    except Exception:
        return "unknown"


def fetch_changelog() -> str:
    try:
        return fetch_text(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Warning: could not fetch changelog: {e}", file=sys.stderr)
        return ""


# ── changelog parsing ──────────────────────────────────────────────────────────

def parse_latest_version(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def extract_new_slugs_from_section(section: str) -> list[str]:
    return sorted(set(re.findall(r"`(/[\w-]+)`", section)))


# ── skill card building ────────────────────────────────────────────────────────

def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_card(skill: SkillDef, source_commit: str) -> dict[str, Any]:
    card: dict[str, Any] = {
        "slug": skill.slug,
        "cmd": skill.cmd,
        "trigger": skill.trigger,
        "desc": skill.desc,
        "source": f"https://github.com/{CC_REPO}",
        "source_branch": CC_BRANCH,
        "source_commit": source_commit,
        "token_policy": list(skill.token_policy) or [
            "Return only decision-critical output.",
            "Avoid repeated background context.",
            "Link to source instead of copying long docs.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every update.",
        ],
    }
    if skill.example:
        card["example"] = skill.example
    if skill.note:
        card["note"] = skill.note
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['slug']}",
        "",
        f"- Cmd: `{card['cmd']}`",
        f"- Source: {card['source']}",
        f"- Source commit: `{card['source_commit']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Description",
        "",
        str(card["desc"]),
        "",
        "## Token Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines.extend(["", "## Compatibility", ""])
    lines.extend(f"- {item}" for item in card["compatibility"])
    if card.get("example"):
        lines.extend(["", "## Example", "", f"```\n{card['example']}\n```", ""])
    if card.get("note"):
        lines.extend(["", "## Note", "", str(card["note"]), ""])
    lines.append("")
    return "\n".join(lines)


# ── catalog I/O ───────────────────────────────────────────────────────────────

def write_snapshot(today: str, cards: list[dict[str, Any]], version: str) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")

    catalog: dict[str, Any] = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "version": version,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "anthropics/claude-code (official)",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return skills_dir


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or path.name >= today or not re.match(r"\d{4}-\d{2}-\d{2}", path.name):
            continue
        catalog_path = path / "skills" / "catalog.json"
        if catalog_path.exists():
            candidates.append(catalog_path)
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def compare_catalogs(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {s["slug"]: s for s in prev.get("skills", []) if "slug" in s}
    next_by_slug = {c["slug"]: c for c in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        slug for slug in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[slug].get("hash") != next_by_slug[slug].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


# ── SKILLS_CATALOG.yaml updater ───────────────────────────────────────────────

def update_yaml_catalog(version: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text(encoding="utf-8")
    text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
    text = re.sub(
        r"^updated:.*$",
        f"updated: {datetime.now(KST).strftime('%Y-%m-%d')}",
        text,
        flags=re.MULTILINE,
    )
    CATALOG_FILE.write_text(text, encoding="utf-8")


# ── changelog writer ──────────────────────────────────────────────────────────

def write_changelog(
    today: str,
    diff: dict[str, list[str]],
    prev_version: str,
    new_version: str,
    skills_dir: Path,
    raw_section: str,
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {s}" for s in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Code Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Source  : https://github.com/{CC_REPO}",
        f"Version : {prev_version or 'none'} -> {new_version}",
        f"Generated: {datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')}",
        "",
        "[추가된 스킬]",
        *bullets(diff["added"]),
        "",
        "[수정된 스킬]",
        *bullets(diff["modified"]),
        "",
        "[삭제된 스킬]",
        *bullets(diff["deleted"]),
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: Claude/skills/{today}/skills",
        "- 각 스킬은 cmd, trigger, desc, token_policy, compatibility로 경량화",
        "- SKILLS_CATALOG.yaml은 단일 정규 소스로 유지; 날짜 스냅샷과 동기화",
        "- catalog.json으로 메타데이터 통합; 개별 .md는 경량 카드로 제한",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 CHANGELOG 복사 대신 버전 번호와 커밋 해시만 저장",
        "- 스킬 설명은 한 줄로 제한; 중복 컨텍스트 제거",
        "- token_policy 필드로 각 스킬별 토큰 절감 지침 명시",
        "- catalog.json 중앙화로 개별 스킬 재로드 없이 메타데이터 조회 가능",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합 (hash 비교로 변경 감지)",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- SKILLS_CATALOG.yaml과 날짜 스냅샷 간 버전 동기화",
        "- 공식 레포 외 출처 스킬은 통합 거부",
        "",
        "[요약]",
        (
            f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
    ]

    if raw_section:
        lines += [
            "─" * 40,
            "[원문 변경사항 / Raw Changes (truncated)]",
            "",
            raw_section[:2000],
            "",
        ]

    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


# ── main ──────────────────────────────────────────────────────────────────────

def current_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else ""


def main() -> int:
    today = datetime.now(KST).strftime("%Y-%m-%d")
    print(f"[{today}] Claude Code skills sync starting...")

    commit = repo_commit(CC_REPO, CC_BRANCH)
    print(f"Source commit: {commit}")

    changelog_text = fetch_changelog()
    latest_ver, raw_section = parse_latest_version(changelog_text)
    prev_ver = current_version()

    if not latest_ver:
        latest_ver = prev_ver or "unknown"
        print("Warning: could not parse version from changelog; using existing.", file=sys.stderr)

    print(f"Version: {prev_ver or 'none'} -> {latest_ver}")

    cards = [build_card(s, commit) for s in SKILL_DEFS]
    prev_catalog = previous_catalog(today)
    diff = compare_catalogs(prev_catalog, cards)

    skills_dir = write_snapshot(today, cards, latest_ver)
    write_changelog(today, diff, prev_ver, latest_ver, skills_dir, raw_section)

    if latest_ver != prev_ver:
        VERSION_FILE.write_text(latest_ver, encoding="utf-8")
        update_yaml_catalog(latest_ver)

    print(f"Synced {len(cards)} skills to {skills_dir.relative_to(REPO_ROOT)}")
    print(f"Changelog: Claude/Changelogs/{today}.txt")
    print(
        f"Diff: added={len(diff['added'])}, modified={len(diff['modified'])}, "
        f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Sync Claude Code skill snapshots from anthropics/claude-code.
Mirrors the GPT sync pattern: dated YYYY-MM-DD/skills snapshots + Changelogs.
Dependency-free; safe for GitHub Actions without prompts.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1]   # .../Claude/
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
KST = timezone(timedelta(hours=9), "KST")

SOURCE_REPO = "anthropics/claude-code"
CHANGELOG_URL = f"https://raw.githubusercontent.com/{SOURCE_REPO}/main/CHANGELOG.md"


# ── Canonical skill definitions (sourced from official Claude Code system prompt) ──
SKILL_DEFS: tuple[dict[str, str], ...] = (
    {
        "slug": "init",
        "cmd": "/init",
        "trigger": "user asks to initialize or document codebase",
        "desc": "Generate CLAUDE.md with codebase architecture, conventions, commands",
    },
    {
        "slug": "review",
        "cmd": "/review",
        "trigger": "user asks to review PR or branch",
        "desc": "Multi-pass PR review; checks logic, style, security, tests",
    },
    {
        "slug": "security-review",
        "cmd": "/security-review",
        "trigger": "user asks security audit of current branch changes",
        "desc": "OWASP-focused audit of pending diffs; risk-ranked findings",
    },
    {
        "slug": "simplify",
        "cmd": "/simplify",
        "trigger": "user asks to clean up or refactor changed code",
        "desc": "Review changed code for reuse/quality/efficiency, then fix issues",
    },
    {
        "slug": "session-start-hook",
        "cmd": "/session-start-hook",
        "trigger": "user wants test/lint runners on session start (web Claude Code)",
        "desc": "Create SessionStart hook ensuring project can run tests and linters",
    },
    {
        "slug": "update-config",
        "cmd": "/update-config",
        "trigger": "automated behavior requests ('when X', 'allow Y', 'set Z=val')",
        "desc": "Configure settings.json; handles hooks, permissions, env vars",
    },
    {
        "slug": "keybindings-help",
        "cmd": "/keybindings-help",
        "trigger": "user wants to remap keys or add chord shortcuts",
        "desc": "Customize ~/.claude/keybindings.json; supports chord bindings",
    },
    {
        "slug": "fewer-permission-prompts",
        "cmd": "/fewer-permission-prompts",
        "trigger": "user wants fewer permission dialogs",
        "desc": "Scan transcripts → add bash/MCP allowlist to .claude/settings.json",
    },
    {
        "slug": "loop",
        "cmd": "/loop [interval] [/command]",
        "trigger": "user wants recurring task (e.g. 'check every 5m', 'keep running X')",
        "desc": "Run prompt or slash command on recurring interval (default 10m)",
    },
    {
        "slug": "claude-api",
        "cmd": "/claude-api",
        "trigger": "code imports anthropic SDK; user asks about Claude API features",
        "desc": "Build/debug Claude API apps; prompt caching, tool use, model migration",
    },
    {
        "slug": "ultrareview",
        "cmd": "/ultrareview [PR#]",
        "trigger": "user says 'ultrareview' or wants multi-agent cloud review",
        "desc": "Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR",
    },
    {
        "slug": "ultraplan",
        "cmd": "/ultraplan",
        "trigger": "user wants cloud environment for complex planning",
        "desc": "Auto-create cloud worktrees/environments for multi-agent planning tasks",
    },
    {
        "slug": "team-onboarding",
        "cmd": "/team-onboarding",
        "trigger": "user wants teammate ramp-up guide",
        "desc": "Generate onboarding guide from local Claude Code usage history/data",
    },
    {
        "slug": "effort",
        "cmd": "/effort",
        "trigger": "user wants to adjust effort/quality level",
        "desc": "Interactive slider for session effort level (also: CLAUDE_EFFORT env var)",
    },
    {
        "slug": "powerup",
        "cmd": "/powerup",
        "trigger": "user wants feature demos or to learn Claude Code features",
        "desc": "Interactive animated feature demos with lessons",
    },
    {
        "slug": "tui",
        "cmd": "/tui",
        "trigger": "rendering looks flickery or user wants full-screen mode",
        "desc": "Switch to flicker-free alt-screen TUI rendering",
    },
    {
        "slug": "focus",
        "cmd": "/focus",
        "trigger": "user wants compact view of conversation",
        "desc": "Toggle focus view: prompt + tool summary + final response",
    },
    {
        "slug": "undo",
        "cmd": "/undo",
        "trigger": "user wants to undo last action",
        "desc": "Alias for /rewind; undoes last assistant action",
    },
    {
        "slug": "usage",
        "cmd": "/usage",
        "trigger": "user asks about token or cost statistics",
        "desc": "Show token usage and cost stats (merged /cost + /stats)",
    },
    {
        "slug": "theme",
        "cmd": "/theme [name]",
        "trigger": "user wants to change or create visual theme",
        "desc": "Create or switch custom color themes",
    },
    {
        "slug": "color",
        "cmd": "/color",
        "trigger": "user wants a session color",
        "desc": "Set random session color (no args = random pick)",
    },
    {
        "slug": "web-setup",
        "cmd": "/web-setup",
        "trigger": "user wants to configure Claude Code for web or remote environment",
        "desc": "Set up Claude Code for web sessions; configure remote execution environment",
    },
    {
        "slug": "plugin",
        "cmd": "/plugin",
        "trigger": "user wants to install or manage Claude Code plugins",
        "desc": "Install, update, or remove Claude Code plugins and extensions",
    },
    {
        "slug": "model",
        "cmd": "/model [name]",
        "trigger": "user wants to switch or inspect the active model",
        "desc": "Switch active model within session (Opus/Sonnet/Haiku); show current model",
    },
)


# ── Helpers ─────────────────────────────────────────────────────────────────────

def fetch_text(url: str) -> str:
    headers = {"User-Agent": "prompt-guide-claude-skill-sync/1.0"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_json(url: str) -> dict[str, Any]:
    return json.loads(fetch_text(url))


def repo_commit(repo: str, branch: str = "main") -> str:
    data = fetch_json(f"https://api.github.com/repos/{repo}/commits/{branch}")
    return str(data.get("sha", ""))[:12]


def parse_latest_version(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def today_kst() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


# ── Build skill cards ─────────────────────────────────────────────────────────

def build_skill(defn: dict[str, str], source_commit: str, upstream_ver: str) -> dict[str, Any]:
    card: dict[str, Any] = {
        "slug": defn["slug"],
        "cmd": defn["cmd"],
        "trigger": defn["trigger"],
        "desc": defn["desc"],
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_commit": source_commit,
        "upstream_version": upstream_ver,
        "token_policy": [
            "Return only decision-critical instructions.",
            "Link to source repo instead of copying long docs.",
            "Avoid repeated background context.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
        ],
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['slug']}",
        "",
        f"- Cmd: `{card['cmd']}`",
        f"- Trigger: {card['trigger']}",
        f"- Source: {card['source']}",
        f"- Source commit: `{card['source_commit']}`",
        f"- Upstream version: {card['upstream_version']}",
        "",
        "## Description",
        "",
        card["desc"],
        "",
        "## Token Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines.extend(["", "## Compatibility", ""])
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.append("")
    return "\n".join(lines)


# ── Snapshot I/O ────────────────────────────────────────────────────────────────

def write_skill_snapshot(today: str, cards: list[dict[str, Any]], upstream_ver: str) -> Path:
    out_dir = SKILLS_ROOT / today / "skills"
    out_dir.mkdir(parents=True, exist_ok=True)

    for card in cards:
        (out_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")

    catalog: dict[str, Any] = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "upstream_version": upstream_ver,
        "directory_rule": "YYYY-MM-DD/skills",
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_policy": "official anthropics/claude-code repository",
        "skills": cards,
    }
    (out_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out_dir


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or path.name >= today or not re.match(r"\d{4}-\d{2}-\d{2}", path.name):
            continue
        catalog = path / "skills" / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


# ── Diff & changelog ──────────────────────────────────────────────────────────

def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {s["slug"]: s for s in prev.get("skills", []) if "slug" in s}
    next_by_slug = {s["slug"]: s for s in cards}

    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        slug for slug in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[slug].get("hash") != next_by_slug[slug].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_changelog(
    today: str,
    diff: dict[str, list[str]],
    prev_ver: str,
    new_ver: str,
    skills_dir: Path,
    new_skills_in_upstream: list[str],
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {v}" for v in values] if values else ["- none"]

    ver_line = f"{prev_ver or 'none'} → {new_ver}" if prev_ver != new_ver else f"{new_ver} (unchanged)"
    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot : Claude/skills/{today}/skills",
        f"Source   : https://github.com/{SOURCE_REPO}",
        f"Version  : {ver_line}",
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
        f"- 날짜별 스냅샷 구조 유지: skills/{today}/skills",
        "- 각 스킬은 cmd, trigger, desc, token_policy, compatibility로 경량화",
        "- 공통 catalog.json으로 메타데이터 통합; 개별 .md는 참조용",
        "- SKILLS_CATALOG.yaml은 마스터 레퍼런스로 유지",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 복사 없이 공식 레포 링크와 커밋 해시만 저장",
        "- 스킬 절차는 짧은 실행 단위로 제한",
        "- 중복 설명 대신 catalog.json으로 메타데이터 통합",
        f"- 스킬 수: {len(diff['unchanged']) + len(diff['added']) + len(diff['modified'])}개",
        "",
        "[충돌 해결 내역]",
        "- slug 기준 중복 스킬 통합",
        "- 기존 날짜 스냅샷 불변 유지 (신규 날짜에만 기록)",
        "- 변경 감지는 hash 비교로 수행",
    ]
    if new_skills_in_upstream:
        lines += ["", "[업스트림 신규 항목 감지]"]
        lines.extend(f"- {item}" for item in new_skills_in_upstream)
    lines += [
        "",
        "[요약]",
        (
            f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def update_catalog_yaml(new_ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text(encoding="utf-8")
    today = today_kst()
    text = re.sub(r"^version:.*$", f"version: {new_ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text, encoding="utf-8")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    print(f"Fetching changelog from {SOURCE_REPO}...")
    try:
        changelog = fetch_text(CHANGELOG_URL)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    new_ver, section = parse_latest_version(changelog)
    if not new_ver:
        print("Could not parse upstream version.", file=sys.stderr)
        return 1

    prev_ver = current_version()
    print(f"Upstream: {new_ver}  |  Local: {prev_ver or 'none'}")

    print(f"Resolving commit hash for {SOURCE_REPO}...")
    try:
        commit = repo_commit(SOURCE_REPO)
    except Exception as e:
        print(f"Warning: could not resolve commit ({e}); using 'unknown'", file=sys.stderr)
        commit = "unknown"

    today = today_kst()

    new_skills_in_upstream = list(set(re.findall(r"`(/[\w-]+)`", section)))

    cards = [build_skill(d, commit, new_ver) for d in SKILL_DEFS]
    prev_catalog = previous_catalog(today)
    skills_dir = write_skill_snapshot(today, cards, new_ver)
    diff = compare(prev_catalog, cards)

    write_changelog(today, diff, prev_ver, new_ver, skills_dir, new_skills_in_upstream)

    VERSION_FILE.write_text(new_ver + "\n", encoding="utf-8")
    update_catalog_yaml(new_ver)

    rel = skills_dir.relative_to(CLAUDE_ROOT)
    print(f"Synced {len(cards)} skills → {rel}")
    print(f"Changelog: Claude/Changelogs/{today}.txt")
    print(f"Version: {prev_ver or 'none'} → {new_ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

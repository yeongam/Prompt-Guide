#!/usr/bin/env python3
"""Sync Claude Code skill cards from official Anthropic sources.

Dependency-free and non-interactive for GitHub Actions use.
Mirrors the structure of GPT/scripts/sync_openai_skills.py.
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


CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CATALOG_PATH = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_PATH = SKILLS_ROOT / ".version"
KST = timezone(timedelta(hours=9), "KST")

NPM_REGISTRY_URL = "https://registry.npmjs.org/@anthropic-ai/claude-code/latest"
GITHUB_RELEASES_URL = "https://api.github.com/repos/anthropics/claude-code/releases"
GITHUB_LATEST_RELEASE_URL = "https://api.github.com/repos/anthropics/claude-code/releases/latest"


@dataclass(frozen=True)
class SkillDef:
    slug: str
    cmd: str
    trigger: str
    desc: str
    example: str = ""


# Canonical skill list — kept in sync with SKILLS_CATALOG.yaml
SKILL_DEFS: tuple[SkillDef, ...] = (
    SkillDef(
        slug="init",
        cmd="/init",
        trigger="user asks to initialize or document codebase",
        desc="Generate CLAUDE.md with codebase architecture, conventions, commands",
    ),
    SkillDef(
        slug="review",
        cmd="/review",
        trigger="user asks to review PR or branch",
        desc="Multi-pass PR review; checks logic, style, security, tests",
    ),
    SkillDef(
        slug="security-review",
        cmd="/security-review",
        trigger="user asks security audit of current branch changes",
        desc="OWASP-focused audit of pending diffs; outputs risk-ranked findings",
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
    ),
    SkillDef(
        slug="ultrareview",
        cmd="/ultrareview [PR#]",
        trigger='user says "ultrareview" or wants multi-agent review',
        desc="Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR",
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
        desc="Toggle focus view: prompt + tool summary + final response only",
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
        slug="deep-research",
        cmd="/deep-research",
        trigger="user wants multi-source fact-checked research report",
        desc="Fan-out web searches, fetch sources, adversarially verify, synthesize cited report",
    ),
    SkillDef(
        slug="code-review",
        cmd="/code-review",
        trigger="user wants code review with optional PR comment or auto-fix",
        desc="Review diff for bugs and cleanups; --comment posts inline PR review, --fix applies fixes",
    ),
    SkillDef(
        slug="verify",
        cmd="/verify",
        trigger="user wants to verify a change works in the real app",
        desc="Run app and observe behavior to confirm fix or feature works end-to-end",
    ),
    SkillDef(
        slug="run",
        cmd="/run",
        trigger="user wants to run or start the app",
        desc="Launch and drive project app; screenshots or confirms changes in real app",
    ),
)

TOKEN_POLICY = [
    "One-line description per skill; no background context in output.",
    "Reference source version for audit; omit if tokens are critical.",
    "Link to release notes instead of copying upstream docs.",
    "Return only decision-critical guidance or commands.",
]

COMPATIBILITY = [
    "Do not overwrite existing dated skill snapshots.",
    "Integrate only if slug is unique or content hash changed.",
    "Preserve changelog evidence for every generated update.",
    "Do not modify GPT or other non-Claude directories.",
]


def _request_json(url: str) -> dict[str, Any]:
    headers: dict[str, str] = {
        "Accept": "application/json",
        "User-Agent": "prompt-guide-claude-skill-sync",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and "github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_npm_version() -> str:
    try:
        data = _request_json(NPM_REGISTRY_URL)
        return str(data.get("version", ""))
    except Exception:
        return ""


def fetch_latest_release_notes() -> tuple[str, str]:
    """Return (tag_name, release_body) for the latest GitHub release."""
    try:
        data = _request_json(GITHUB_LATEST_RELEASE_URL)
        return str(data.get("tag_name", "")), str(data.get("body", ""))
    except Exception:
        return "", ""


def _card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill_card(skill: SkillDef, source_version: str) -> dict[str, Any]:
    card: dict[str, Any] = {
        "slug": skill.slug,
        "cmd": skill.cmd,
        "trigger": skill.trigger,
        "desc": skill.desc,
        "source": "https://github.com/anthropics/claude-code",
        "source_version": source_version,
        "token_policy": TOKEN_POLICY,
        "compatibility": COMPATIBILITY,
    }
    if skill.example:
        card["example"] = skill.example
    card["hash"] = _card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['slug']}",
        "",
        f"- Cmd: `{card['cmd']}`",
        f"- Source: {card['source']}",
        f"- Source version: `{card['source_version']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Description",
        "",
        card["desc"],
    ]
    if card.get("example"):
        lines += ["", f"Example: `{card['example']}`"]
    lines += [
        "",
        "## Token Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.append("")
    return "\n".join(lines)


def current_date() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def read_current_version() -> str:
    if VERSION_PATH.exists():
        return VERSION_PATH.read_text(encoding="utf-8").strip()
    return ""


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or path.name >= today or not re.match(r"\d{4}-\d{2}-\d{2}$", path.name):
            continue
        cat = path / "skills" / "catalog.json"
        if cat.exists():
            candidates.append(cat)
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def write_snapshot(today: str, cards: list[dict[str, Any]]) -> Path:
    snap_dir = SKILLS_ROOT / today / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (snap_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog: dict[str, Any] = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source": "https://github.com/anthropics/claude-code",
        "source_policy": "official Anthropic claude-code repository only",
        "skills": cards,
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return snap_dir


def compare_skills(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {s["slug"]: s for s in prev.get("skills", []) if "slug" in s}
    next_by_slug = {s["slug"]: s for s in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        slug
        for slug in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[slug].get("hash") != next_by_slug[slug].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def update_version_file(version: str) -> None:
    VERSION_PATH.write_text(version + "\n", encoding="utf-8")


def write_changelog(
    today: str,
    diff: dict[str, list[str]],
    snap_dir: Path,
    old_version: str,
    new_version: str,
) -> Path:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {s}" for s in values] if values else ["- none"]

    version_note = (
        f"- 버전 업데이트: {old_version} → {new_version}"
        if old_version and new_version and old_version != new_version
        else f"- 현재 버전: {new_version or old_version}"
    )

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        "Source: https://github.com/anthropics/claude-code",
        f"Version: {new_version or old_version}",
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
        "- 단일 catalog.json으로 메타데이터 통합",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 복사 제거; 공식 레포 링크와 버전만 저장",
        "- 스킬 설명은 1줄로 제한; 배경 컨텍스트 미포함",
        "- 중복 설명 대신 공통 catalog.json으로 통합",
        version_note,
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "- GPT/Claude 디렉토리 간 상호 침범 없음",
        "",
        "[요약]",
        (
            f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
    ]
    out = CHANGELOGS_ROOT / f"{today}.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    dupes: set[str] = set()
    for c in cards:
        slug = str(c.get("slug", ""))
        if slug in seen:
            dupes.add(slug)
        seen.add(slug)
    if dupes:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(dupes))}")


def main() -> int:
    today = current_date()
    old_version = read_current_version()

    # Fetch latest version from npm
    npm_version = fetch_npm_version()
    new_version = npm_version or old_version

    # Fetch release notes if version changed (for future skill discovery)
    release_tag, release_body = "", ""
    if npm_version and npm_version != old_version:
        release_tag, release_body = fetch_latest_release_notes()

    # Build skill cards
    cards = [build_skill_card(s, new_version) for s in SKILL_DEFS]
    ensure_unique(cards)

    # Load previous snapshot for diffing
    prev = previous_catalog(today)

    # Write dated snapshot
    snap_dir = write_snapshot(today, cards)

    # Diff
    diff = compare_skills(prev, cards)

    # Update version file if changed
    if npm_version and npm_version != old_version:
        update_version_file(npm_version)

    # Write changelog
    log_path = write_changelog(today, diff, snap_dir, old_version, new_version)

    print(f"Synced {len(cards)} Claude skills to {snap_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {log_path.relative_to(CLAUDE_ROOT)}")
    if release_tag:
        print(f"New release detected: {release_tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

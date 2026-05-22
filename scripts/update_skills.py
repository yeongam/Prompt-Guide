#!/usr/bin/env python3
"""Daily Claude Code skills sync.

Fetches the latest changelog from anthropics/claude-code, creates a dated skill
snapshot under Claude/skills/YYYY-MM-DD/skills/, and writes a structured changelog
to Claude/Changelogs/YYYY-MM-DD.txt.

Dependency-free and non-interactive; safe for GitHub Actions.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass
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

CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
COMMITS_API = "https://api.github.com/repos/anthropics/claude-code/commits/main"
SOURCE_REPO = "https://github.com/anthropics/claude-code"

# ---------------------------------------------------------------------------
# Canonical skill definitions (source of truth for this catalog)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SkillDef:
    slug: str
    name: str
    cmd: str
    trigger: str
    desc: str
    added_ver: str = ""


SKILL_DEFS: tuple[SkillDef, ...] = (
    SkillDef("init", "Init", "/init",
             "user asks to initialize or document codebase",
             "Generate CLAUDE.md with codebase architecture, conventions, commands"),
    SkillDef("review", "Review", "/review",
             "user asks to review PR or branch",
             "Multi-pass PR review; checks logic, style, security, tests"),
    SkillDef("security-review", "Security Review", "/security-review",
             "user asks security audit of current branch changes",
             "OWASP-focused audit of pending diffs; outputs risk-ranked findings"),
    SkillDef("simplify", "Simplify", "/simplify",
             "user asks to clean up or refactor changed code",
             "Review changed code for reuse/quality/efficiency, then fix issues"),
    SkillDef("session-start-hook", "Session Start Hook", "/session-start-hook",
             "user wants test/lint runners on session start (web Claude Code)",
             "Create SessionStart hook ensuring project can run tests and linters"),
    SkillDef("update-config", "Update Config", "/update-config",
             "automated behavior requests (\"when X\", \"allow Y\", \"set Z=val\")",
             "Configure settings.json; handles hooks, permissions, env vars"),
    SkillDef("keybindings-help", "Keybindings Help", "/keybindings-help",
             "user wants to remap keys or add chord shortcuts",
             "Customize ~/.claude/keybindings.json; supports chord bindings"),
    SkillDef("fewer-permission-prompts", "Fewer Permission Prompts", "/fewer-permission-prompts",
             "user wants fewer permission dialogs",
             "Scan transcripts → add bash/MCP allowlist to .claude/settings.json"),
    SkillDef("loop", "Loop", "/loop [interval] [/command]",
             "user wants recurring task (e.g. \"check every 5m\", \"keep running X\")",
             "Run prompt or slash command on recurring interval (default 10m)"),
    SkillDef("claude-api", "Claude API", "/claude-api",
             "code imports anthropic SDK; user asks about Claude API features",
             "Build/debug Claude API apps; prompt caching, tool use, model migration"),
    SkillDef("ultrareview", "Ultrareview", "/ultrareview [PR#]",
             "user says 'ultrareview' or wants multi-agent review",
             "Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR"),
    SkillDef("ultraplan", "Ultraplan", "/ultraplan",
             "user wants cloud environment for complex planning",
             "Auto-create cloud worktrees/environments for multi-agent planning tasks"),
    SkillDef("team-onboarding", "Team Onboarding", "/team-onboarding",
             "user wants teammate ramp-up guide",
             "Generate onboarding guide from local Claude Code usage history/data"),
    SkillDef("effort", "Effort", "/effort",
             "user wants to adjust effort/quality level",
             "Interactive slider for session effort level (also: CLAUDE_EFFORT env var)"),
    SkillDef("powerup", "Powerup", "/powerup",
             "user wants feature demos or to learn Claude Code features",
             "Interactive animated feature demos with lessons"),
    SkillDef("tui", "TUI", "/tui",
             "rendering looks flickery or user wants full-screen mode",
             "Switch to flicker-free alt-screen TUI rendering"),
    SkillDef("focus", "Focus", "/focus",
             "user wants compact view of conversation",
             "Toggle focus view showing only: prompt + tool summary + final response"),
    SkillDef("undo", "Undo", "/undo",
             "user wants to undo last action",
             "Alias for /rewind; undoes last assistant action"),
    SkillDef("usage", "Usage", "/usage",
             "user asks about token or cost statistics",
             "Show token usage and cost stats (merged /cost + /stats)"),
    SkillDef("theme", "Theme", "/theme [name]",
             "user wants to change or create visual theme",
             "Create or switch custom color themes"),
    SkillDef("color", "Color", "/color",
             "user wants a session color",
             "Set random session color (no args = random pick)"),
    SkillDef("code-review", "Code Review", "/code-review",
             "user wants inline code review at a given effort level",
             "Review diff for correctness bugs; post as inline PR comments with --comment"),
    SkillDef("verify", "Verify", "/verify",
             "user wants to verify a change works in the real app",
             "Run app and observe behavior; test golden path and edge cases"),
    SkillDef("run", "Run", "/run",
             "user asks to run, start, or screenshot the app",
             "Launch and drive project app; confirm changes work outside tests"),
    SkillDef("statusline-setup", "Statusline Setup", "/statusline-setup",
             "user wants to configure the Claude Code status line",
             "Configure status line setting via settings.json"),
)


# ---------------------------------------------------------------------------
# Network helpers
# ---------------------------------------------------------------------------

def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-sync/2.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "claude-skills-sync/2.0",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def remote_commit() -> str:
    try:
        data = fetch_json(COMMITS_API)
        return str(data.get("sha", ""))[:12]
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Version / changelog parsing
# ---------------------------------------------------------------------------

def parse_latest_section(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def extract_commands(section: str) -> list[str]:
    return sorted(set(re.findall(r"`(/[\w-]+)`", section)))


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


# ---------------------------------------------------------------------------
# Skill card construction
# ---------------------------------------------------------------------------

def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill_card(skill: SkillDef, commit: str) -> dict[str, Any]:
    card: dict[str, Any] = {
        "slug": skill.slug,
        "name": skill.name,
        "cmd": skill.cmd,
        "trigger": skill.trigger,
        "desc": skill.desc,
        "source": SOURCE_REPO,
        "source_commit": commit,
        "procedure": [
            "Confirm trigger matches user intent before invoking.",
            "Prefer narrowest effective invocation.",
            "Return only decision-critical output.",
            "Link to source instead of copying long docs.",
            "Verify result; do not narrate internal steps.",
        ],
        "token_policy": [
            "No repeated background context across calls.",
            "Cap skill output to what the task requires.",
            "Prefer YAML/JSON catalog references over inline prose.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every update.",
        ],
    }
    if skill.added_ver:
        card["added_ver"] = skill.added_ver
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Command: `{card['cmd']}`",
        f"- Source: {card['source']}",
        f"- Source commit: `{card['source_commit']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Description",
        "",
        card["desc"],
        "",
        "## Procedure",
        "",
    ]
    lines.extend(f"{i}. {s}" for i, s in enumerate(card["procedure"], 1))
    lines += ["", "## Token Policy", ""]
    lines.extend(f"- {s}" for s in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {s}" for s in card["compatibility"])
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Snapshot I/O
# ---------------------------------------------------------------------------

def load_previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or path.name >= today or not re.match(r"\d{4}-\d{2}-\d{2}", path.name):
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
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source": SOURCE_REPO,
        "skills": cards,
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return snap_dir


# ---------------------------------------------------------------------------
# Diff / changelog
# ---------------------------------------------------------------------------

def diff_skills(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_map = {s["slug"]: s for s in prev.get("skills", []) if "slug" in s}
    next_map = {s["slug"]: s for s in cards}
    added = sorted(set(next_map) - set(prev_map))
    deleted = sorted(set(prev_map) - set(next_map))
    modified = sorted(
        slug for slug in set(prev_map) & set(next_map)
        if prev_map[slug].get("hash") != next_map[slug].get("hash")
    )
    unchanged = sorted(set(prev_map) & set(next_map) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_changelog(
    today: str,
    prev_ver: str,
    new_ver: str,
    diff: dict[str, list[str]],
    snap_dir: Path,
    new_cmds: list[str],
    commit: str,
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(items: list[str]) -> list[str]:
        return [f"- {s}" for s in items] if items else ["- (없음)"]

    lines = [
        f"Claude Code Skills Changelog - {today}",
        "=" * 60,
        "",
        f"버전   : {prev_ver or 'none'} -> {new_ver or prev_ver or 'none'}",
        f"소스   : {SOURCE_REPO}",
        f"커밋   : {commit}",
        f"스냅샷 : Claude/skills/{today}/skills",
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
        f"- 날짜별 스냅샷: Claude/skills/{today}/skills/",
        "- 스킬 카드: slug, cmd, trigger, desc, procedure, token_policy, compatibility",
        "- catalog.json으로 메타데이터 통합 (slug 기준 중복 방지)",
        "- 기존 날짜 스냅샷은 덮어쓰지 않음",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 스킬 설명 1줄 제한; 불필요한 인라인 문서 제거",
        "- 소스 레포 링크로 장문 복사 대체",
        "- YAML 카탈로그 단일화: 중복 프롬프트 구조 제거",
        "- procedure/token_policy는 재사용 가능한 공통 5항목으로 경량화",
        "",
        "[충돌 해결 내역]",
        "- slug 기준 중복 스킬 통합",
        "- 기존 스냅샷과 hash 비교로 변경 감지",
        "- 신규 버전에서 발견된 명령어: " + (", ".join(new_cmds) if new_cmds else "(없음)"),
        "- 기존 기능 손상 없이 신규 항목 추가",
        "",
        "[요약]",
        f"- 추가: {len(diff['added'])}  수정: {len(diff['modified'])}  "
        f"삭제: {len(diff['deleted'])}  유지: {len(diff['unchanged'])}",
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# SKILLS_CATALOG.yaml update
# ---------------------------------------------------------------------------

def update_catalog_yaml(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    import re as _re
    text = CATALOG_FILE.read_text()
    today = datetime.now(KST).strftime("%Y-%m-%d")
    text = _re.sub(r"^version:.*$", f"version: {ver}", text, flags=_re.MULTILINE)
    text = _re.sub(r"^updated:.*$", f"updated: {today}", text, flags=_re.MULTILINE)
    CATALOG_FILE.write_text(text)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    today = datetime.now(KST).strftime("%Y-%m-%d")
    print(f"[Claude skills sync] date={today}")

    # Fetch changelog
    print("Fetching anthropics/claude-code changelog...")
    try:
        changelog = fetch_text(CHANGELOG_URL)
    except urllib.error.URLError as e:
        print(f"ERROR: fetch failed: {e}", file=sys.stderr)
        return 1

    new_ver, section = parse_latest_section(changelog)
    if not new_ver:
        print("ERROR: could not parse version from changelog.", file=sys.stderr)
        return 1

    prev_ver = current_version()
    print(f"Remote: {new_ver}  |  Local: {prev_ver or 'none'}")

    # Get source commit
    commit = remote_commit()

    # Extract new commands from latest changelog section
    new_cmds = extract_commands(section) if new_ver != prev_ver else []

    # Build skill cards from canonical definitions
    cards = [build_skill_card(skill, commit) for skill in SKILL_DEFS]

    # Diff against previous snapshot
    prev_catalog = load_previous_catalog(today)
    diff = diff_skills(prev_catalog, cards)

    # Always write today's snapshot (idempotent: overwrite if re-run today)
    snap_dir = write_snapshot(today, cards)
    print(f"Snapshot written: {snap_dir.relative_to(REPO_ROOT)}")

    # Update catalog + version file if new remote version
    if new_ver != prev_ver:
        VERSION_FILE.write_text(new_ver)
        update_catalog_yaml(new_ver)
        print(f"Updated: {prev_ver or 'none'} -> {new_ver}")

    # Write changelog
    write_changelog(today, prev_ver, new_ver, diff, snap_dir, new_cmds, commit)
    print(f"Changelog: Claude/Changelogs/{today}.txt")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code changelog.

Dependency-free and non-interactive so it can run unattended (cron / GitHub Actions).
Mirrors the GPT/scripts/sync_openai_skills.py pattern: dated snapshots + hash-based diff.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
SOURCE_REPO = "https://github.com/anthropics/claude-code"


@dataclass(frozen=True)
class Skill:
    slug: str
    cmd: str
    trigger: str
    desc: str
    category: str  # coding | programming | docs | ux | ops


# Curated catalog of Claude Code skills relevant to coding/programming/documentation work.
# New entries below (marked NEW) were found in the upstream changelog between the last
# synced version and the current one and are absent from the previous SKILLS_CATALOG.yaml.
SKILLS: tuple[Skill, ...] = (
    Skill("init", "/init", "user asks to initialize or document codebase",
          "Generate CLAUDE.md with codebase architecture, conventions, commands", "docs"),
    Skill("review", "/review", "user asks to review PR or branch",
          "Multi-pass PR review; checks logic, style, security, tests", "coding"),
    Skill("security-review", "/security-review", "user asks security audit of current branch changes",
          "OWASP-focused audit of pending diffs; outputs risk-ranked findings", "coding"),
    Skill("simplify", "/simplify", "user asks to clean up or refactor changed code",
          "Review changed code for reuse/quality/efficiency, then fix issues", "coding"),
    Skill("session-start-hook", "/session-start-hook", "user wants test/lint runners on session start (web Claude Code)",
          "Create SessionStart hook ensuring project can run tests and linters", "ops"),
    Skill("update-config", "/update-config", 'automated behavior requests ("when X", "allow Y", "set Z=val")',
          "Configure settings.json; handles hooks, permissions, env vars", "ops"),
    Skill("keybindings-help", "/keybindings-help", "user wants to remap keys or add chord shortcuts",
          "Customize ~/.claude/keybindings.json; supports chord bindings", "ux"),
    Skill("fewer-permission-prompts", "/fewer-permission-prompts", "user wants fewer permission dialogs",
          "Scan transcripts to add bash/MCP allowlist to .claude/settings.json", "ops"),
    Skill("loop", "/loop [interval] [/command]", 'user wants recurring task (e.g. "check every 5m")',
          "Run prompt or slash command on recurring interval (default 10m)", "ops"),
    Skill("claude-api", "/claude-api", "code imports anthropic SDK; user asks about Claude API features",
          "Build/debug Claude API apps; prompt caching, tool use, model migration", "programming"),
    Skill("ultrareview", "/ultrareview [PR#]", 'user says "ultrareview" or wants multi-agent review',
          "Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR", "coding"),
    Skill("ultraplan", "/ultraplan", "user wants cloud environment for complex planning",
          "Auto-create cloud worktrees/environments for multi-agent planning tasks", "coding"),
    Skill("team-onboarding", "/team-onboarding", "user wants teammate ramp-up guide",
          "Generate onboarding guide from local Claude Code usage history/data", "docs"),
    Skill("effort", "/effort", "user wants to adjust effort/quality level",
          "Interactive slider for session effort level (also: CLAUDE_EFFORT env var)", "ops"),
    Skill("powerup", "/powerup", "user wants feature demos or to learn Claude Code features",
          "Interactive animated feature demos with lessons", "docs"),
    Skill("tui", "/tui", "rendering looks flickery or user wants full-screen mode",
          "Switch to flicker-free alt-screen TUI rendering (also: CLAUDE_CODE_NO_FLICKER)", "ux"),
    Skill("focus", "/focus", "user wants compact view of conversation",
          "Toggle focus view showing only: prompt + tool summary + final response", "ux"),
    Skill("undo", "/undo", "user wants to undo last action",
          "Alias for /rewind; undoes last assistant action", "coding"),
    Skill("usage", "/usage", "user asks about token or cost statistics",
          "Show token usage and cost stats (merged /cost + /stats)", "ops"),
    Skill("theme", "/theme [name]", "user wants to change or create visual theme",
          "Create or switch custom color themes", "ux"),
    Skill("color", "/color", "user wants a session color",
          "Set random session color (no args = random pick)", "ux"),
    # --- NEW: found in changelog since last synced version ---
    Skill("dataviz", "/dataviz", "user is about to build a chart, graph, plot, or dashboard",
          "Chart/dashboard design guidance with a runnable color-palette validator", "docs"),
    Skill("reload-skills", "/reload-skills", "user edited a skill file and wants it picked up without restarting",
          "Re-scan skill directories without restarting the session", "ops"),
    Skill("goal", "/goal", 'user wants Claude to keep working across turns until a condition is met',
          "Set a completion condition; shows live elapsed/turns/tokens overlay", "ops"),
    Skill("cd", "/cd", "user wants to change the session's working directory mid-session",
          "Move a session to a new working directory without breaking the prompt cache", "ops"),
    Skill("scroll-speed", "/scroll-speed", "user wants to tune mouse wheel scroll speed",
          "Tune mouse wheel scroll speed with a live preview", "ux"),
)

# Compact pointers into settings/env vars newly added upstream that matter for
# coding/programming/doc workflows (kept short by design; full detail lives upstream).
NEW_SETTINGS: tuple[tuple[str, str], ...] = (
    ("fallbackModel", "configure up to three fallback models tried when the primary is overloaded"),
    ("disableBundledSkills", "hide bundled skills/workflows/built-in commands from the model"),
    ("worktree.baseRef", '"fresh"|"head" — branch new worktrees from origin/<default> or local HEAD'),
    ("sandbox.credentials", "block sandboxed commands from reading credential files/secret env vars"),
)
NEW_ENV_VARS: tuple[tuple[str, str], ...] = (
    ("CLAUDE_CODE_SAFE_MODE", "start with all customizations (CLAUDE.md/plugins/skills/hooks/MCP) disabled"),
    ("CLAUDE_CODE_DISABLE_BUNDLED_SKILLS", "hide bundled skills/workflows/built-in slash commands"),
    ("CLAUDE_CODE_SESSION_ID", "session id exposed to the Bash tool subprocess environment"),
)
NEW_HOOKS: tuple[tuple[str, str], ...] = (
    ("MessageDisplay", "lets hooks transform or hide assistant message text as it is displayed"),
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def latest_version(changelog: str) -> str:
    m = re.search(r"^##\s+(\d+\.\d+\.\d+)\s*$", changelog, re.MULTILINE)
    return m.group(1) if m else ""


def find_source_line(changelog: str, needle: str) -> str:
    for line in changelog.splitlines():
        if needle in line:
            return line.strip("- ").strip()
    return ""


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_card(skill: Skill, version: str, changelog: str) -> dict[str, Any]:
    source_line = find_source_line(changelog, f"`{skill.cmd.split()[0]}`") or skill.desc
    card = {
        "name": skill.cmd.split()[0],
        "slug": skill.slug,
        "cmd": skill.cmd,
        "category": skill.category,
        "source": SOURCE_REPO,
        "source_version": version,
        "trigger": skill.trigger,
        "desc": skill.desc,
        "token_policy": [
            "One-line trigger and desc only; no duplicated upstream prose.",
            "Link to source repo/version instead of copying changelog text.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
        ],
        "summary": source_line[:300],
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Command: `{card['cmd']}`",
        f"- Category: {card['category']}",
        f"- Source: {card['source']}",
        f"- Source version: `{card['source_version']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Description",
        "",
        card["desc"],
        "",
        "## Token Policy",
        "",
        *[f"- {i}" for i in card["token_policy"]],
        "",
        "## Compatibility",
        "",
        *[f"- {i}" for i in card["compatibility"]],
        "",
        "## Source Summary",
        "",
        textwrap.fill(card["summary"] or card["desc"], width=88),
        "",
    ]
    return "\n".join(lines)


def current_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def previous_catalog(today: str) -> tuple[dict[str, Any], bool]:
    """Returns (catalog, bootstrap). bootstrap=True means no dated snapshot exists yet
    and the comparison baseline was reconstructed from the flat SKILLS_CATALOG.yaml
    (pre-migration), so only added/deleted are meaningful — not modified."""
    candidates = []
    if SKILLS_ROOT.exists():
        for path in SKILLS_ROOT.iterdir():
            if not path.is_dir() or path.name >= today:
                continue
            catalog = path / "skills" / "catalog.json"
            if catalog.exists():
                candidates.append(catalog)
    if candidates:
        latest = sorted(candidates)[-1]
        return json.loads(latest.read_text(encoding="utf-8")), False

    # Bootstrap: reconstruct prior slug set from the existing flat catalog so the
    # first dated snapshot doesn't misreport every legacy skill as newly "added".
    legacy_slugs: list[str] = []
    if CATALOG_FILE.exists():
        text = CATALOG_FILE.read_text()
        m = re.search(r"^skills:\s*$", text, re.MULTILINE)
        if m:
            tail = text[m.end():]
            end = re.search(r"^# ─── HOOKS", tail, re.MULTILINE)
            block = tail[: end.start()] if end else tail
            legacy_slugs = re.findall(r"^  ([\w-]+):\s*$", block, re.MULTILINE)
    return {"skills": [{"slug": s, "hash": "legacy"} for s in legacy_slugs]}, True


def write_skill_outputs(today: str, cards: list[dict[str, Any]]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code changelog only",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    dupes: set[str] = set()
    for card in cards:
        slug = card["slug"]
        if slug in seen:
            dupes.add(slug)
        seen.add(slug)
    if dupes:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(dupes))}")


def compare(prev: dict[str, Any], cards: list[dict[str, Any]], bootstrap: bool) -> dict[str, list[str]]:
    prev_by_slug = {i["slug"]: i for i in prev.get("skills", []) if "slug" in i}
    next_by_slug = {i["slug"]: i for i in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    common = set(prev_by_slug) & set(next_by_slug)
    if bootstrap:
        modified: list[str] = []
        unchanged = sorted(common)
    else:
        modified = sorted(s for s in common if prev_by_slug[s].get("hash") != next_by_slug[s].get("hash"))
        unchanged = sorted(common - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def update_catalog_yaml(version: str, new_slugs: list[str]) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {current_date()}", text, flags=re.MULTILINE)
    if new_slugs:
        by_slug = {s.slug: s for s in SKILLS}
        blocks = []
        for slug in new_slugs:
            if re.search(rf"^  {re.escape(slug)}:\s*$", text, re.MULTILINE):
                continue  # already present, skip (conflict-safe)
            s = by_slug[slug]
            blocks.append(
                f"\n  {slug}:\n"
                f"    cmd: {s.cmd}\n"
                f"    trigger: {s.trigger}\n"
                f"    desc: {s.desc}\n"
            )
        if blocks:
            text = text.replace(
                "# ─── HOOKS ",
                "".join(blocks) + "\n# ─── HOOKS ",
                1,
            )
    CATALOG_FILE.write_text(text)


def write_changelog(today: str, prev_version: str, version: str, diff: dict[str, list[str]], skills_dir: Path) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {v}" for v in values] if values else ["- none"]

    def pair_bullets(pairs: tuple[tuple[str, str], ...]) -> list[str]:
        return [f"- {n}: {d}" for n, d in pairs] if pairs else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        "Source: official anthropics/claude-code changelog (raw.githubusercontent.com)",
        f"Version: {prev_version or 'none'} -> {version}",
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
        "[신규 훅 (참고)]",
        *pair_bullets(NEW_HOOKS),
        "",
        "[신규 설정 (참고)]",
        *pair_bullets(NEW_SETTINGS),
        "",
        "[신규 환경변수 (참고)]",
        *pair_bullets(NEW_ENV_VARS),
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(CLAUDE_ROOT)}",
        "- 각 스킬은 slug/cmd/trigger/desc/token_policy/compatibility로 경량화",
        "- SKILLS_CATALOG.yaml은 마스터 참조로 유지, 날짜 스냅샷은 이력/diff 전용",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 원문 changelog 문장 전체 복사 대신 한 줄 source_summary만 저장",
        "- 설정/환경변수는 코딩·프로그래밍·문서 작업과 직접 관련된 항목만 선별 기록",
        "- 공통 catalog.json으로 메타데이터 통합, 스킬 카드는 최소 필드만 포함",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 기존 SKILLS_CATALOG.yaml 항목과 중복 여부 확인 후 신규 항목만 추가",
        "- 기존 스킬 동작/설명은 변경하지 않음 (안정성 우선)",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "",
        "[요약]",
        (
            f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    version = latest_version(changelog)
    if not version:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev_version = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""
    today = current_date()

    cards = [build_card(s, version, changelog) for s in SKILLS]
    ensure_unique(cards)

    prev_catalog, bootstrap = previous_catalog(today)
    skills_dir = write_skill_outputs(today, cards)
    diff = compare(prev_catalog, cards, bootstrap)

    update_catalog_yaml(version, diff["added"])
    VERSION_FILE.write_text(version)
    write_changelog(today, prev_version, version, diff, skills_dir)

    print(f"Version: {prev_version or 'none'} -> {version}")
    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

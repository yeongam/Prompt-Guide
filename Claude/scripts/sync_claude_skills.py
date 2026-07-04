#!/usr/bin/env python3
"""Daily Claude Code skills updater.

Fetches CHANGELOG.md from anthropics/claude-code, refreshes the coding /
programming / documentation skill catalog, and snapshots it under a
YYYY-MM-DD/skills directory (mirrors the GPT/scripts routine). Non-interactive
so it can run unattended from a scheduled routine or GitHub Actions.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
LEGACY_VERSION_FILE = SKILLS_ROOT / ".version"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
SOURCE_REPO = "anthropics/claude-code"


@dataclass(frozen=True)
class Skill:
    slug: str
    cmd: str
    category: str  # coding | programming | documentation | productivity | ui
    trigger: str
    desc: str
    since_version: str = ""


SKILLS: tuple[Skill, ...] = (
    Skill("init", "/init", "documentation", "user asks to initialize or document codebase",
          "Generate CLAUDE.md with codebase architecture, conventions, commands"),
    Skill("review", "/review", "coding", "user asks to review a GitHub PR",
          "PR review; now shares the /code-review medium engine"),
    Skill("code-review", "/code-review [effort] [--comment|--fix]", "coding",
          "user asks for a bug-focused review of the current diff",
          "Reports correctness bugs at a chosen effort level; --comment posts inline PR "
          "comments, --fix applies findings to the working tree. Replaced /simplify's old "
          "bug-hunting role; five cleanup finders were merged into one (~25% fewer tokens)",
          "2.1.130-2.1.201"),
    Skill("security-review", "/security-review", "coding",
          "user asks for a security audit of current branch changes",
          "OWASP-focused audit of pending diffs; outputs risk-ranked findings"),
    Skill("simplify", "/simplify", "coding", "user asks to clean up or refactor changed code",
          "Cleanup-only review (reuse, simplification, efficiency, altitude); now invokes "
          "/code-review --fix instead of running its own bug-hunting pass",
          "2.1.130-2.1.201"),
    Skill("dataviz", "/dataviz", "programming", "user is about to build a chart or dashboard",
          "Chart and dashboard design guidance with a runnable color-palette validator",
          "2.1.130-2.1.201"),
    Skill("deep-research", "/deep-research", "documentation",
          "user wants a deep, multi-source, fact-checked report",
          "Fan-out web research with adversarial claim verification and a cited synthesis"),
    Skill("workflows", "/workflows", "programming",
          "user wants deterministic multi-agent orchestration",
          "Dynamic workflows: orchestrates tens to hundreds of background agents "
          "(pipeline/parallel fan-out) for large or multi-step tasks",
          "2.1.130-2.1.201"),
    Skill("goal", "/goal", "productivity", "user wants Claude to keep working until a condition holds",
          "Set a completion condition; Claude keeps working across turns until it's met, "
          "with a live elapsed/turns/tokens overlay",
          "2.1.130-2.1.201"),
    Skill("reload-skills", "/reload-skills", "programming",
          "skill files changed on disk mid-session",
          "Re-scan skill directories without restarting the session",
          "2.1.130-2.1.201"),
    Skill("session-start-hook", "/session-start-hook", "programming",
          "user wants test/lint runners on session start (web Claude Code)",
          "Create a SessionStart hook that ensures the project can run tests and linters"),
    Skill("update-config", "/update-config", "programming",
          "automated behavior requests (\"when X\", \"allow Y\", \"set Z=val\")",
          "Configure settings.json: hooks, permissions, env vars"),
    Skill("keybindings-help", "/keybindings-help", "productivity",
          "user wants to remap keys or add chord shortcuts",
          "Customize ~/.claude/keybindings.json; supports chord bindings"),
    Skill("fewer-permission-prompts", "/fewer-permission-prompts", "programming",
          "user wants fewer permission dialogs",
          "Scan transcripts, add a Bash/MCP allowlist to .claude/settings.json"),
    Skill("loop", "/loop [interval] [/command]", "productivity",
          "user wants a recurring task (e.g. \"check every 5m\")",
          "Run a prompt or slash command on a recurring interval (default 10m)"),
    Skill("claude-api", "/claude-api", "programming",
          "code imports the Anthropic SDK; user asks about Claude API features",
          "Build/debug Claude API apps: prompt caching, tool use, model migration"),
    Skill("ultraplan", "/ultraplan", "programming",
          "user wants a cloud environment for complex planning",
          "Auto-create cloud worktrees/environments for multi-agent planning tasks"),
    Skill("team-onboarding", "/team-onboarding", "documentation",
          "user wants a teammate ramp-up guide",
          "Generate an onboarding guide from local Claude Code usage history"),
    Skill("effort", "/effort", "productivity", "user wants to adjust effort/quality level",
          "Interactive slider for session effort level (also: CLAUDE_EFFORT env var)"),
    Skill("powerup", "/powerup", "documentation", "user wants feature demos",
          "Interactive animated feature demos with lessons"),
    Skill("tui", "/tui", "ui", "rendering looks flickery or user wants full-screen mode",
          "Switch to flicker-free alt-screen TUI rendering"),
    Skill("focus", "/focus", "ui", "user wants a compact view of the conversation",
          "Toggle focus view: prompt + tool summary + final response only"),
    Skill("undo", "/undo", "productivity", "user wants to undo the last action",
          "Alias for /rewind; undoes the last assistant action"),
    Skill("usage", "/usage", "productivity", "user asks about token or cost statistics",
          "Show token usage and cost stats (merged /cost + /stats)"),
    Skill("theme", "/theme [name]", "ui", "user wants to change or create a visual theme",
          "Create or switch custom color themes"),
    Skill("color", "/color", "ui", "user wants a session color",
          "Set a random session color (no args = random pick)"),
)

SETTINGS: dict[str, dict[str, str]] = {
    "skillOverrides": {"type": "off | user-invocable-only | name-only",
                        "desc": "off=hidden from model+slash, user-invocable-only=hidden from model, name-only=minimal exposure"},
    "disableBundledSkills": {"type": "bool",
                              "desc": "Hide bundled skills, workflows, and built-in slash commands from the model",
                              "since": "2.1.130-2.1.201"},
    "disableSkillShellExecution": {"type": "bool", "desc": "Disable inline shell execution within skill definitions"},
    "showThinkingSummaries": {"type": "bool", "desc": "Control thinking summary generation in responses"},
}

ENV: dict[str, str] = {
    "CLAUDE_EFFORT": "Current effort level; usable in skill template strings as ${CLAUDE_EFFORT}",
    "CLAUDE_CODE_DISABLE_BUNDLED_SKILLS": "1 = hide bundled skills/workflows/built-in commands from the model",
    "CLAUDE_CODE_NO_FLICKER": "1 = enable alt-screen flicker-free rendering (same as /tui)",
}

MODELS: dict[str, str] = {
    "default": "claude-sonnet-5",
    "opus": "claude-opus-4-8",
    "sonnet": "claude-sonnet-5",
    "haiku": "claude-haiku-4-5-20251001",
}

SKILL_FRONTMATTER_NOTE = (
    "Skills/slash commands can set `disallowed-tools` in frontmatter to remove tools while "
    "active; SessionStart hooks can return `reloadSkills: true` to re-scan skills mid-session."
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_latest_version(changelog: str) -> str:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    return m.group(1) if m else ""


def legacy_version() -> str:
    if LEGACY_VERSION_FILE.exists():
        return LEGACY_VERSION_FILE.read_text().strip()
    return ""


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill_card(skill: Skill, version: str) -> dict[str, Any]:
    card = {
        "name": skill.slug,
        "slug": skill.slug,
        "cmd": skill.cmd,
        "category": skill.category,
        "trigger": skill.trigger,
        "desc": skill.desc,
        "since_version": skill.since_version,
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_ref": f"CHANGELOG.md @ {version}",
        "token_policy": [
            "One-line trigger/desc only; no upstream prose duplication.",
            "Full behavior detail lives in the skill's own SKILL.md, not this catalog.",
        ],
        "compatibility": [
            "Do not overwrite prior dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
        ],
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['cmd']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Category: {card['category']}",
        f"- Source: {card['source']} ({card['source_ref']})",
        f"- Trigger: {card['trigger']}",
    ]
    if card["since_version"]:
        lines.append(f"- Changed in: {card['since_version']}")
    lines += ["", "## Description", "", card["desc"], "", "## Token Policy", ""]
    lines += [f"- {t}" for t in card["token_policy"]]
    lines += ["", "## Compatibility", ""]
    lines += [f"- {c}" for c in card["compatibility"]]
    lines.append("")
    return "\n".join(lines)


def previous_catalog(today: str) -> dict[str, Any]:
    candidates = []
    if SKILLS_ROOT.exists():
        for path in SKILLS_ROOT.iterdir():
            if not path.is_dir() or path.name >= today:
                continue
            catalog = path / "skills" / "catalog.json"
            if catalog.exists():
                candidates.append(catalog)
    if candidates:
        return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))

    # First run: fall back to the legacy flat SKILLS_CATALOG.yaml as the diff baseline.
    legacy_yaml = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
    if legacy_yaml.exists():
        text = legacy_yaml.read_text()
        block = re.search(r"^skills:\s*\n(.*?)(?=^\S)", text, flags=re.MULTILINE | re.DOTALL)
        slugs = re.findall(r"^  ([a-zA-Z][\w-]*):\s*$", block.group(1), flags=re.MULTILINE) if block else []
        return {"skills": [{"slug": s, "hash": "legacy"} for s in slugs]}
    return {}


def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {c["slug"]: c for c in prev.get("skills", []) if "slug" in c}
    next_by_slug = {c["slug"]: c for c in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        s for s in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[s].get("hash") != next_by_slug[s].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_skill_outputs(today: str, version: str) -> tuple[Path, list[dict[str, Any]]]:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    cards = [build_skill_card(s, version) for s in SKILLS]
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": today,
        "version": version,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "skill_frontmatter_note": SKILL_FRONTMATTER_NOTE,
        "settings": SETTINGS,
        "env": ENV,
        "models": MODELS,
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir, cards


def write_changelog(today: str, version: str, prev_version: str, diff: dict[str, list[str]], skills_dir: Path) -> Path:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {s}" for s in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot : Claude/skills/{today}/skills",
        f"Version  : {prev_version or 'none (legacy flat catalog)'} -> {version}",
        f"Source   : https://github.com/{SOURCE_REPO}/blob/main/CHANGELOG.md",
        "",
        "[추가된 스킬 / Added]",
        *bullets(diff["added"]),
        "",
        "[수정된 스킬 / Modified]",
        *bullets(diff["modified"]),
        "",
        "[삭제된 스킬 / Deleted]",
        *bullets(diff["deleted"]),
        "",
        "[최적화된 구조 / Structure]",
        f"- 날짜별 스냅샷 구조로 전환: {skills_dir.relative_to(CLAUDE_ROOT)} (기존 평면 SKILLS_CATALOG.yaml 대체)",
        "- 스킬별 개별 카드(.md) + catalog.json으로 분리하여 GPT 루틴과 동일한 구조 사용",
        "- settings/env/models는 catalog.json에 압축 보관, 반복 설명 제거",
        "",
        "[토큰 절감 관련 변경 사항 / Token Savings]",
        "- 스킬 카드는 trigger/desc/since_version만 유지, 원문 changelog 문단은 복사하지 않음",
        "- 카드별 token_policy로 SKILL.md 본문 참조를 명시해 중복 설명 방지",
        "- 변경 감지는 hash 비교로 수행, 불필요한 재작성 방지",
        "",
        "[충돌 해결 내역 / Conflicts]",
        "- slug 기준 중복 스킬 없음 확인 (review vs code-review는 별도 slug로 분리 유지)",
        "- 기존 SKILLS_CATALOG.yaml/.version은 신규 날짜 스냅샷의 최초 diff 기준선으로만 사용",
        "- 이전 날짜 스냅샷은 덮어쓰지 않고 신규 날짜 디렉토리에 기록",
        "",
        "[요약 / Summary]",
        f"- added={len(diff['added'])}, modified={len(diff['modified'])}, "
        f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}",
        "",
    ]
    out = CHANGELOGS_ROOT / f"{today}.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    version = parse_latest_version(changelog)
    if not version:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev_version = legacy_version()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    prev = previous_catalog(today)
    skills_dir, cards = write_skill_outputs(today, version)
    diff = compare(prev, cards)
    changelog_path = write_changelog(today, version, prev_version, diff, skills_dir)

    print(f"Version: {prev_version or 'none'} -> {version}")
    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {changelog_path.relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

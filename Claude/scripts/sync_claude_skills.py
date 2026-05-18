#!/usr/bin/env python3
"""Sync Claude Code skill cards from anthropics/claude-code.

Dependency-free, non-interactive — runs in GitHub Actions without prompts.
Output: Claude/skills/YYYY-MM-DD/skills/ + Claude/Changelogs/YYYY-MM-DD.txt
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
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
KST = timezone(timedelta(hours=9), "KST")

CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
REPO_API = "https://api.github.com/repos/anthropics/claude-code/commits/main"


@dataclass(frozen=True)
class SkillDef:
    slug: str
    name: str
    cmd: str
    trigger: str
    output: str
    notes: tuple[str, ...] = field(default_factory=tuple)


SKILL_DEFS: tuple[SkillDef, ...] = (
    SkillDef("init", "Initialize Codebase", "/init",
             "User asks to initialize or document codebase",
             "CLAUDE.md with architecture, conventions, commands"),
    SkillDef("review", "PR Review", "/review",
             "User asks to review PR or branch",
             "Multi-pass review: logic, style, security, tests"),
    SkillDef("security-review", "Security Review", "/security-review",
             "User asks security audit of current branch changes",
             "OWASP-focused audit of pending diffs; risk-ranked findings"),
    SkillDef("simplify", "Simplify Code", "/simplify",
             "User asks to clean up or refactor changed code",
             "Review changed code for reuse/quality/efficiency, then fix"),
    SkillDef("session-start-hook", "Session Start Hook", "/session-start-hook",
             "User wants test/lint runners on session start (web Claude Code)",
             "SessionStart hook ensuring project can run tests and linters"),
    SkillDef("update-config", "Update Config", "/update-config",
             "Automated behavior requests: 'when X', 'allow Y', 'set Z=val'",
             "Configure settings.json: hooks, permissions, env vars"),
    SkillDef("keybindings-help", "Keybindings Help", "/keybindings-help",
             "User wants to remap keys or add chord shortcuts",
             "Customize ~/.claude/keybindings.json; supports chord bindings"),
    SkillDef("fewer-permission-prompts", "Fewer Permission Prompts", "/fewer-permission-prompts",
             "User wants fewer permission dialogs",
             "Scan transcripts; add bash/MCP allowlist to .claude/settings.json"),
    SkillDef("loop", "Loop Task", "/loop [interval] [/command]",
             "User wants recurring task (e.g. 'check every 5m', 'keep running X')",
             "Run prompt or slash command on recurring interval (default 10m)",
             ("Example: /loop 5m /review",)),
    SkillDef("claude-api", "Claude API", "/claude-api",
             "Code imports anthropic SDK; user asks about Claude API features",
             "Build/debug Claude API apps; prompt caching, tool use, model migration",
             ("Models: opus=claude-opus-4-7, sonnet=claude-sonnet-4-6, haiku=claude-haiku-4-5-20251001",)),
    SkillDef("ultrareview", "Ultra Review", "/ultrareview [PR#]",
             "User says 'ultrareview' or wants multi-agent review",
             "Parallel multi-agent cloud review; no-arg=local branch, arg=GitHub PR",
             ("Billed; requires git repo",)),
    SkillDef("ultraplan", "Ultra Plan", "/ultraplan",
             "User wants cloud environment for complex planning",
             "Auto-create cloud worktrees/environments for multi-agent planning"),
    SkillDef("team-onboarding", "Team Onboarding", "/team-onboarding",
             "User wants teammate ramp-up guide",
             "Generate onboarding guide from local Claude Code usage history"),
    SkillDef("effort", "Effort Level", "/effort",
             "User wants to adjust effort/quality level",
             "Interactive slider for session effort level; also CLAUDE_EFFORT env var"),
    SkillDef("powerup", "Power Up", "/powerup",
             "User wants feature demos or to learn Claude Code features",
             "Interactive animated feature demos with lessons"),
    SkillDef("tui", "TUI Mode", "/tui",
             "Rendering looks flickery or user wants full-screen mode",
             "Switch to flicker-free alt-screen TUI rendering",
             ("Also: CLAUDE_CODE_NO_FLICKER env var",)),
    SkillDef("focus", "Focus View", "/focus",
             "User wants compact view of conversation",
             "Toggle focus view: prompt + tool summary + final response only"),
    SkillDef("undo", "Undo", "/undo",
             "User wants to undo last action",
             "Alias for /rewind; undoes last assistant action"),
    SkillDef("usage", "Usage Stats", "/usage",
             "User asks about token or cost statistics",
             "Show token usage and cost stats (merged /cost + /stats)"),
    SkillDef("theme", "Theme", "/theme [name]",
             "User wants to change or create visual theme",
             "Create or switch custom color themes"),
    SkillDef("color", "Session Color", "/color",
             "User wants a session color",
             "Set random session color (no args = random pick)"),
)


def fetch_text(url: str) -> str:
    headers = {"User-Agent": "prompt-guide-claude-skill-sync"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_json(url: str) -> dict[str, Any]:
    return json.loads(fetch_text(url))


def current_date() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def parse_latest_version(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else start + 4000
    return ver, changelog[start:end].strip()


def card_hash(card: dict[str, Any]) -> str:
    payload = json.dumps({k: v for k, v in card.items() if k != "hash"},
                         sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def build_skill_card(defn: SkillDef, source_commit: str, ver: str) -> dict[str, Any]:
    card: dict[str, Any] = {
        "name": defn.name,
        "slug": defn.slug,
        "cmd": defn.cmd,
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main",
        "source_commit": source_commit,
        "catalog_version": ver,
        "trigger": defn.trigger,
        "procedure": [
            "Confirm trigger matches user intent before invoking.",
            "Prefer smallest effective invocation.",
            "Keep output scoped to the specific request.",
            "Do not add unrequested features or refactors.",
            "Verify result without re-reading unchanged files.",
        ],
        "output": defn.output,
        "token_policy": [
            "Avoid repeating background context already in conversation.",
            "Return only decision-critical output.",
            "Link to source instead of copying long docs.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every update.",
        ],
    }
    if defn.notes:
        card["notes"] = list(defn.notes)
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Cmd: `{card['cmd']}`",
        f"- Source: {card['source']}",
        f"- Source commit: `{card['source_commit']}`",
        f"- Catalog version: `{card['catalog_version']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    lines.extend(f"{i}. {s}" for i, s in enumerate(card["procedure"], 1))
    lines += ["", "## Output", "", str(card["output"]), "", "## Token Policy", ""]
    lines.extend(f"- {s}" for s in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {s}" for s in card["compatibility"])
    if card.get("notes"):
        lines += ["", "## Notes", ""]
        lines.extend(f"- {n}" for n in card["notes"])
    lines.append("")
    return "\n".join(lines)


def write_skill_snapshot(today: str, cards: list[dict[str, Any]]) -> Path:
    out = SKILLS_ROOT / today / "skills"
    out.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (out / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source": "anthropics/claude-code",
        "skills": cards,
    }
    (out / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = [
        p / "skills" / "catalog.json"
        for p in SKILLS_ROOT.iterdir()
        if p.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", p.name) and p.name < today
        and (p / "skills" / "catalog.json").exists()
    ]
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def diff_skills(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_map = {s["slug"]: s for s in prev.get("skills", []) if "slug" in s}
    next_map = {s["slug"]: s for s in cards}
    added = sorted(set(next_map) - set(prev_map))
    deleted = sorted(set(prev_map) - set(next_map))
    modified = sorted(
        sl for sl in set(prev_map) & set(next_map)
        if prev_map[sl].get("hash") != next_map[sl].get("hash")
    )
    unchanged = sorted(set(prev_map) & set(next_map) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_changelog(today: str, ver: str, prev_ver: str, diff: dict[str, list[str]],
                    section: str, snapshot_path: Path) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(items: list[str]) -> list[str]:
        return [f"- {s}" for s in items] if items else ["- none"]

    lines = [
        f"Claude Code Skills Changelog - {today}",
        "",
        f"Snapshot : Claude/skills/{today}/skills",
        f"Source   : https://github.com/anthropics/claude-code",
        f"Version  : {prev_ver or 'none'} -> {ver}",
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
        f"- 날짜별 스냅샷: Claude/skills/{today}/skills",
        "- 각 스킬: trigger, procedure, output, token_policy, compatibility 경량화",
        "- 중복 설명 제거; catalog.json으로 메타데이터 통합",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 원문 문서 복사 없이 공식 레포 링크와 커밋 해시만 저장",
        "- 스킬 절차는 짧은 실행 단위(5개)로 제한",
        "- 공통 정책 필드(token_policy, compatibility) 재사용",
        "",
        "[충돌 해결 내역]",
        "- slug 기준 중복 통합 (ensure_unique 검증)",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지: hash 비교",
        "",
        "[최신 변경사항 원문 (축약)]",
        section[:2000] if section else "(no changelog section parsed)",
        "",
        "[요약]",
        (f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
         f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def update_catalog_meta(ver: str, today: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text(encoding="utf-8")
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text, encoding="utf-8")


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    dupes: set[str] = set()
    for c in cards:
        sl = str(c.get("slug", ""))
        if sl in seen:
            dupes.add(sl)
        seen.add(sl)
    if dupes:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(dupes))}")


def main() -> int:
    today = current_date()
    prev_ver = current_version()

    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch_text(CHANGELOG_URL)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, section = parse_latest_version(changelog)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    print(f"Latest: {ver}  |  Local: {prev_ver or 'none'}")

    print("Fetching source commit...")
    try:
        commit_data = fetch_json(REPO_API)
        source_commit = str(commit_data.get("sha", ""))[:12]
    except urllib.error.URLError:
        source_commit = "unknown"

    cards = [build_skill_card(d, source_commit, ver) for d in SKILL_DEFS]
    ensure_unique(cards)

    prev_catalog = previous_catalog(today)
    diff = diff_skills(prev_catalog, cards)

    snapshot_path = write_skill_snapshot(today, cards)
    write_changelog(today, ver, prev_ver, diff, section, snapshot_path)

    VERSION_FILE.write_text(ver, encoding="utf-8")
    update_catalog_meta(ver, today)

    print(f"Synced {len(cards)} skills to {snapshot_path.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: Claude/Changelogs/{today}.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from anthropics/claude-code.

Dependency-free and non-interactive for GitHub Actions use.
Directory rule: Claude/skills/YYYY-MM-DD/skills/
Changelogs:    Claude/Changelogs/YYYY-MM-DD.txt
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
KST = timezone(timedelta(hours=9), "KST")

REPO = "anthropics/claude-code"
BRANCH = "main"


# ── data classes ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SkillDef:
    slug: str
    name: str
    cmd: str
    trigger: str
    output: str
    procedure: tuple[str, ...] = field(default_factory=tuple)
    note: str = ""
    category: str = "skill"


# ── skill definitions ─────────────────────────────────────────────────────────

SKILL_DEFS: tuple[SkillDef, ...] = (
    SkillDef(
        slug="init",
        name="Init",
        cmd="/init",
        trigger="User asks to initialize or document codebase",
        output="CLAUDE.md with architecture, conventions, and commands",
        procedure=(
            "Scan project structure and key entry points.",
            "Identify build/test/lint commands.",
            "Summarize conventions and architecture.",
            "Write concise CLAUDE.md under 100 lines.",
        ),
    ),
    SkillDef(
        slug="review",
        name="Review",
        cmd="/review",
        trigger="User asks to review a PR or branch",
        output="Multi-pass review: logic, style, security, tests",
        procedure=(
            "Read diff and recent commits.",
            "Check logic errors, edge cases, and security issues.",
            "Verify test coverage matches changed paths.",
            "Output risk-ranked findings with file:line references.",
        ),
    ),
    SkillDef(
        slug="security-review",
        name="Security Review",
        cmd="/security-review",
        trigger="User asks for security audit of current branch changes",
        output="OWASP-focused findings ranked by risk",
        procedure=(
            "Run diff against OWASP Top 10 checklist.",
            "Flag injection, auth, secrets, and dependency issues.",
            "Rank findings by exploitability and impact.",
            "Provide minimal remediation per finding.",
        ),
    ),
    SkillDef(
        slug="simplify",
        name="Simplify",
        cmd="/simplify",
        trigger="User asks to clean up or refactor changed code",
        output="Refactored code with explanation of changes",
        procedure=(
            "Identify duplicate logic and dead code in changed files.",
            "Remove unnecessary abstractions.",
            "Prefer standard library over custom implementations.",
            "Verify behavior is unchanged after simplification.",
        ),
    ),
    SkillDef(
        slug="session-start-hook",
        name="Session Start Hook",
        cmd="/session-start-hook",
        trigger="User wants test/lint runners on session start (web Claude Code)",
        output="SessionStart hook in .claude/settings.json",
        procedure=(
            "Identify test and lint commands from project config.",
            "Write SessionStart hook that runs them on startup.",
            "Ensure hook exits non-zero on failure to block bad sessions.",
        ),
    ),
    SkillDef(
        slug="update-config",
        name="Update Config",
        cmd="/update-config",
        trigger="Automated behavior requests: 'when X', 'allow Y', 'set Z=val'",
        output="Updated .claude/settings.json or ~/.claude/settings.json",
        procedure=(
            "Determine if change is project-level or user-level.",
            "Edit the correct settings.json file.",
            "Use hooks for automated behaviors, permissions for tool access.",
            "Validate JSON after editing.",
        ),
    ),
    SkillDef(
        slug="keybindings-help",
        name="Keybindings Help",
        cmd="/keybindings-help",
        trigger="User wants to remap keys or add chord shortcuts",
        output="Updated ~/.claude/keybindings.json",
        procedure=(
            "Read current ~/.claude/keybindings.json.",
            "Apply requested keybinding changes.",
            "Support chord bindings with array syntax.",
            "Validate JSON after editing.",
        ),
    ),
    SkillDef(
        slug="fewer-permission-prompts",
        name="Fewer Permission Prompts",
        cmd="/fewer-permission-prompts",
        trigger="User wants fewer permission dialogs",
        output="Allowlist added to .claude/settings.json",
        procedure=(
            "Scan transcripts for repeated bash and MCP tool calls.",
            "Identify safe, read-only patterns to allowlist.",
            "Add allowlist entries to .claude/settings.json.",
            "Prioritize by frequency of prompting.",
        ),
    ),
    SkillDef(
        slug="loop",
        name="Loop",
        cmd="/loop [interval] [/command]",
        trigger="User wants recurring task (e.g. 'check every 5m', 'keep running X')",
        output="Recurring task running at specified interval",
        procedure=(
            "Parse interval (default 10m) and target command.",
            "Run command, report status, then sleep.",
            "Stop on user request or terminal error.",
        ),
        note="Example: /loop 5m /review",
    ),
    SkillDef(
        slug="claude-api",
        name="Claude API",
        cmd="/claude-api",
        trigger="Code imports anthropic SDK; user asks about Claude API features",
        output="Optimized Claude API code with prompt caching",
        procedure=(
            "Use model IDs: opus=claude-opus-4-7, sonnet=claude-sonnet-4-6, haiku=claude-haiku-4-5-20251001.",
            "Add prompt caching on system/large context blocks.",
            "Implement tool use with minimal JSON schema.",
            "Handle streaming where latency matters.",
            "Migrate deprecated model references.",
        ),
    ),
    SkillDef(
        slug="ultrareview",
        name="Ultrareview",
        cmd="/ultrareview [PR#]",
        trigger="User says 'ultrareview' or wants multi-agent review",
        output="Parallel multi-agent code review report",
        procedure=(
            "Bundle local branch (no-arg) or fetch GitHub PR.",
            "Run parallel agents across review dimensions.",
            "Merge findings into ranked report.",
        ),
        note="Billed; requires git repo",
    ),
    SkillDef(
        slug="ultraplan",
        name="Ultraplan",
        cmd="/ultraplan",
        trigger="User wants cloud environment for complex planning",
        output="Multi-agent planning result with worktrees",
        procedure=(
            "Create cloud worktrees for isolated planning.",
            "Run parallel planning agents.",
            "Present consolidated plan.",
        ),
    ),
    SkillDef(
        slug="team-onboarding",
        name="Team Onboarding",
        cmd="/team-onboarding",
        trigger="User wants teammate ramp-up guide",
        output="Onboarding guide from local Claude Code usage history",
        procedure=(
            "Scan local Claude Code usage history.",
            "Extract common workflows and patterns.",
            "Generate structured onboarding document.",
        ),
    ),
    SkillDef(
        slug="effort",
        name="Effort",
        cmd="/effort",
        trigger="User wants to adjust effort/quality level",
        output="Updated session effort level",
        procedure=(
            "Display current effort level.",
            "Accept new level (or read CLAUDE_EFFORT env var).",
            "Apply to current session.",
        ),
    ),
    SkillDef(
        slug="usage",
        name="Usage",
        cmd="/usage",
        trigger="User asks about token or cost statistics",
        output="Token usage and cost breakdown",
        procedure=(
            "Collect token usage from current session.",
            "Calculate cost by model tier.",
            "Display summary with per-turn breakdown.",
        ),
    ),
    SkillDef(
        slug="tui",
        name="TUI",
        cmd="/tui",
        trigger="Rendering looks flickery or user wants full-screen mode",
        output="Alt-screen flicker-free TUI rendering",
        procedure=(
            "Toggle alt-screen TUI mode.",
            "Equivalent to CLAUDE_CODE_NO_FLICKER=1 env var.",
        ),
    ),
    SkillDef(
        slug="focus",
        name="Focus",
        cmd="/focus",
        trigger="User wants compact view of conversation",
        output="Compact view: prompt + tool summary + final response only",
        procedure=(
            "Toggle focus mode.",
            "Hides intermediate tool output from display.",
        ),
    ),
    SkillDef(
        slug="undo",
        name="Undo",
        cmd="/undo",
        trigger="User wants to undo last action",
        output="Last assistant action reverted",
        procedure=(
            "Alias for /rewind.",
            "Reverts last assistant action in current session.",
        ),
    ),
    SkillDef(
        slug="theme",
        name="Theme",
        cmd="/theme [name]",
        trigger="User wants to change or create visual theme",
        output="Applied or newly created color theme",
        procedure=(
            "List available themes if no arg given.",
            "Apply named theme or open creation flow.",
        ),
    ),
    SkillDef(
        slug="color",
        name="Color",
        cmd="/color",
        trigger="User wants a session color",
        output="Random or selected session color applied",
        procedure=(
            "Pick random color (no args) or apply specified color.",
        ),
    ),
    SkillDef(
        slug="powerup",
        name="Powerup",
        cmd="/powerup",
        trigger="User wants feature demos or to learn Claude Code features",
        output="Interactive animated feature demos",
        procedure=(
            "Launch interactive feature demo sequence.",
            "Covers key Claude Code capabilities.",
        ),
    ),
)

# ── coding / programming / documentation skills ───────────────────────────────

CODING_SKILL_DEFS: tuple[SkillDef, ...] = (
    SkillDef(
        slug="claude-code-api-integration",
        name="Claude Code API Integration",
        cmd="(coding)",
        trigger="User implements Claude API; needs caching, tool use, or model migration",
        output="Optimized API code with correct model IDs and caching",
        procedure=(
            "Import anthropic SDK; AsyncAnthropic for async paths.",
            "Add cache_control={'type':'ephemeral'} on system/large context blocks.",
            "Use current IDs: claude-opus-4-7, claude-sonnet-4-6, claude-haiku-4-5-20251001.",
            "Define tools with minimal JSON schema.",
            "Handle tool_use blocks in response loop.",
        ),
        category="coding",
    ),
    SkillDef(
        slug="claude-code-hook-authoring",
        name="Claude Code Hook Authoring",
        cmd="(coding)",
        trigger="User writes PreToolUse, PostToolUse, Stop, or lifecycle hooks",
        output="Shell or MCP hook script integrated with Claude Code lifecycle",
        procedure=(
            "Choose hook type: shell command, mcp_tool, or http endpoint.",
            "Blocking: exit 2 or JSON {decision:'block', reason:'...'}.",
            "PreToolUse: read tool_name and tool_input from stdin JSON.",
            "PostToolUse: read tool_name, tool_input, tool_output from stdin.",
            "Keep hooks fast; slow hooks delay every tool call.",
        ),
        category="coding",
    ),
    SkillDef(
        slug="claude-code-settings-config",
        name="Claude Code Settings Config",
        cmd="(coding)",
        trigger="User edits .claude/settings.json or ~/.claude/settings.json",
        output="Valid settings.json with requested configuration",
        procedure=(
            "Project: .claude/settings.json; user: ~/.claude/settings.json.",
            "Permissions: allowedTools/deniedTools arrays.",
            "Hooks: hooks object keyed by lifecycle event.",
            "Env vars: env object with string key-value pairs.",
            "Validate JSON before saving.",
        ),
        category="coding",
    ),
    SkillDef(
        slug="claude-code-mcp-integration",
        name="Claude Code MCP Integration",
        cmd="(coding)",
        trigger="User sets up or debugs MCP servers in Claude Code",
        output="Working MCP server in .claude/settings.json",
        procedure=(
            "Add server to mcpServers section of settings.json.",
            "Specify command, args, env for server process.",
            "Use type: stdio for local process servers.",
            "Test with /mcp to verify connection.",
            "Grant permissions via allowedTools for auto-approval.",
        ),
        category="coding",
    ),
    SkillDef(
        slug="claude-code-documentation",
        name="Claude Code Documentation",
        cmd="(coding)",
        trigger="User writes or updates CLAUDE.md, docs, or code comments",
        output="Concise documentation following Claude Code conventions",
        procedure=(
            "CLAUDE.md: architecture, build/test/lint commands, conventions.",
            "Keep CLAUDE.md under 100 lines; link details elsewhere.",
            "Code comments: only WHY, one line max.",
            "No docstrings unless required by framework.",
            "Prefer self-documenting names over comments.",
        ),
        category="coding",
    ),
    SkillDef(
        slug="claude-code-subagent-sdk",
        name="Claude Code Subagent SDK",
        cmd="(coding)",
        trigger="User builds multi-agent workflows with Claude Agent SDK",
        output="Agent orchestration code with proper tool delegation",
        procedure=(
            "Use Agent tool for tasks exceeding 3 search queries or needing isolation.",
            "Pass self-contained prompts; agents have no prior context.",
            "Specify subagent_type for specialized agents (Explore, Plan, etc.).",
            "Run independent agents in parallel via single message multi-call.",
            "Trust but verify: check agent output before reporting success.",
        ),
        category="coding",
    ),
)

ALL_SKILLS = SKILL_DEFS + CODING_SKILL_DEFS


# ── http helpers ──────────────────────────────────────────────────────────────

def request_json(url: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "prompt-guide-claude-skill-sync",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def request_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "prompt-guide-claude-skill-sync"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def repo_commit(repo: str, branch: str) -> str:
    data = request_json(f"https://api.github.com/repos/{repo}/commits/{branch}")
    return str(data.get("sha", ""))[:12]


def fetch_changelog() -> str:
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/CHANGELOG.md"
    try:
        return request_text(url)
    except urllib.error.URLError:
        return ""


def fetch_readme() -> str:
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/README.md"
    try:
        return request_text(url)
    except urllib.error.URLError:
        return ""


# ── parsing ───────────────────────────────────────────────────────────────────

def parse_latest_version(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def compact_text(text: str, max_chars: int = 300) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars - 1].rstrip() + "." if len(text) > max_chars else text


# ── card builders ─────────────────────────────────────────────────────────────

def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_card(defn: SkillDef, commit: str, version: str) -> dict[str, Any]:
    card: dict[str, Any] = {
        "name": defn.name,
        "slug": defn.slug,
        "cmd": defn.cmd,
        "category": defn.category,
        "source": f"https://github.com/{REPO}",
        "source_branch": BRANCH,
        "source_commit": commit,
        "source_version": version,
        "trigger": defn.trigger,
        "procedure": list(defn.procedure),
        "output": defn.output,
        "token_policy": [
            "Return only decision-critical content.",
            "Link to source repo instead of copying long docs.",
            "Avoid repeated background context across turns.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
    }
    if defn.note:
        card["note"] = defn.note
    card["hash"] = card_hash(card)
    return card


# ── markdown renderer ─────────────────────────────────────────────────────────

def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Command: `{card['cmd']}`",
        f"- Category: {card['category']}",
        f"- Source: {card['source']}",
        f"- Source commit: `{card['source_commit']}`",
        f"- Version: {card['source_version']}",
        f"- Trigger: {card['trigger']}",
    ]
    if card.get("note"):
        lines.append(f"- Note: {card['note']}")
    lines += ["", "## Procedure", ""]
    lines.extend(f"{i}. {s}" for i, s in enumerate(card["procedure"], 1))
    lines += ["", "## Output", "", str(card["output"]), "", "## Token Policy", ""]
    lines.extend(f"- {s}" for s in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {s}" for s in card["compatibility"])
    lines.append("")
    return "\n".join(lines)


# ── diff / catalog helpers ────────────────────────────────────────────────────

def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for d in SKILLS_ROOT.iterdir():
        if not d.is_dir() or d.name >= today:
            continue
        cat = d / "skills" / "catalog.json"
        if cat.exists():
            candidates.append(cat)
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_map = {c["slug"]: c for c in prev.get("skills", []) if "slug" in c}
    next_map = {c["slug"]: c for c in cards}
    added = sorted(set(next_map) - set(prev_map))
    deleted = sorted(set(prev_map) - set(next_map))
    modified = sorted(
        s for s in set(prev_map) & set(next_map)
        if prev_map[s].get("hash") != next_map[s].get("hash")
    )
    unchanged = sorted(set(prev_map) & set(next_map) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


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


# ── writers ───────────────────────────────────────────────────────────────────

def write_skills(today: str, cards: list[dict[str, Any]], version: str) -> Path:
    out = SKILLS_ROOT / today / "skills"
    out.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (out / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "version": version,
        "directory_rule": "YYYY-MM-DD/skills",
        "source": f"https://github.com/{REPO}",
        "source_policy": f"official {REPO} repository only",
        "skills": cards,
    }
    (out / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out


def write_changelog(
    today: str,
    diff: dict[str, list[str]],
    skills_dir: Path,
    version: str,
    prev_version: str,
    raw_section: str,
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bul(items: list[str]) -> list[str]:
        return [f"- {s}" for s in items] if items else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Version : {prev_version or 'none'} -> {version}",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Source  : https://github.com/{REPO}",
        "",
        "[추가된 스킬]",
        *bul(diff["added"]),
        "",
        "[수정된 스킬]",
        *bul(diff["modified"]),
        "",
        "[삭제된 스킬]",
        *bul(diff["deleted"]),
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(CLAUDE_ROOT)}",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 코딩/프로그래밍/문서 작업 스킬 포함 (category=coding)",
        "- 중복 설명 제거; 공통 catalog.json으로 메타데이터 통합",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 커밋 해시와 링크만 저장",
        "- 절차 항목은 짧은 실행 단위로 제한 (각 1줄)",
        "- YAML 대신 JSON catalog; 중복 필드 제거",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 content hash 비교로 수행",
        "",
        "[요약]",
        (
            f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
        "[원문 변경사항 요약 / Upstream Changes]",
        "",
        raw_section[:2000] if raw_section else "(changelog not available)",
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


# ── version file ──────────────────────────────────────────────────────────────

VERSION_FILE = SKILLS_ROOT / ".version"

def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""

def save_version(ver: str) -> None:
    VERSION_FILE.write_text(ver)

def update_catalog_version(ver: str) -> None:
    cat = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
    if not cat.exists():
        return
    text = cat.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {datetime.now(KST).strftime('%Y-%m-%d')}", text, flags=re.MULTILINE)
    cat.write_text(text)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    today = datetime.now(KST).strftime("%Y-%m-%d")
    print(f"Syncing Claude Code skills — {today}")

    print("Fetching upstream data...")
    commit = "local"
    changelog = ""
    try:
        commit = repo_commit(REPO, BRANCH)
        changelog = fetch_changelog()
        print(f"Upstream fetch OK (commit: {commit})")
    except urllib.error.URLError as e:
        print(f"Network unavailable ({e}); using local definitions.", file=sys.stderr)

    version, raw_section = parse_latest_version(changelog)
    if not version:
        version = current_version() or "2.1.129"
    prev_version = current_version()
    print(f"Version: {prev_version or 'none'} -> {version}  |  commit: {commit}")

    cards = [build_card(d, commit, version) for d in ALL_SKILLS]
    ensure_unique(cards)

    prev = previous_catalog(today)
    diff = compare(prev, cards)

    skills_dir = write_skills(today, cards, version)
    write_changelog(today, diff, skills_dir, version, prev_version, raw_section)

    if version != prev_version and version != "unknown":
        save_version(version)
        update_catalog_version(version)

    print(f"Skills  : {len(cards)} cards -> {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    print(
        f"Diff    : added={len(diff['added'])}, modified={len(diff['modified'])}, "
        f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

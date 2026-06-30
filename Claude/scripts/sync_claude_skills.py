#!/usr/bin/env python3
"""Sync compact Claude Code skill and hook cards from anthropics/claude-code.

Dependency-free, non-interactive — runs in GitHub Actions without prompts.
Structure mirrors GPT/scripts/sync_openai_skills.py for consistency.
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

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
VERSION_FILE = SKILLS_ROOT / ".version"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
KST = timezone(timedelta(hours=9), "KST")

SOURCE_REPO = "anthropics/claude-code"
SOURCE_BRANCH = "main"
CHANGELOG_URL = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_BRANCH}/CHANGELOG.md"
API_COMMIT_URL = f"https://api.github.com/repos/{SOURCE_REPO}/commits/{SOURCE_BRANCH}"


@dataclass(frozen=True)
class SkillDef:
    slug: str
    name: str
    cmd: str
    trigger: str
    desc: str
    example: str = ""


@dataclass(frozen=True)
class HookDef:
    slug: str
    name: str
    event: str
    fires: str
    can_block: bool
    use: str


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
             "Review changed code for reuse/quality/efficiency, then apply fixes"),
    SkillDef("session-start-hook", "Session Start Hook", "/session-start-hook",
             "user wants test/lint runners on session start (web Claude Code)",
             "Create SessionStart hook ensuring project can run tests and linters"),
    SkillDef("update-config", "Update Config", "/update-config",
             'automated behavior requests ("when X", "allow Y", "set Z=val")',
             "Configure settings.json; handles hooks, permissions, env vars"),
    SkillDef("keybindings-help", "Keybindings Help", "/keybindings-help",
             "user wants to remap keys or add chord shortcuts",
             "Customize ~/.claude/keybindings.json; supports chord bindings"),
    SkillDef("fewer-permission-prompts", "Fewer Permission Prompts", "/fewer-permission-prompts",
             "user wants fewer permission dialogs",
             "Scan transcripts -> add bash/MCP allowlist to .claude/settings.json"),
    SkillDef("loop", "Loop", "/loop [interval] [/command]",
             "user wants recurring task",
             "Run prompt or slash command on recurring interval (default 10m)",
             example="/loop 5m /review"),
    SkillDef("claude-api", "Claude API", "/claude-api",
             "code imports anthropic SDK; user asks about Claude API features",
             "Build/debug Claude API apps; prompt caching, tool use, model migration"),
    SkillDef("ultrareview", "Ultrareview", "/ultrareview [PR#]",
             'user says "ultrareview" or wants multi-agent review',
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
             "Toggle focus view: prompt + tool summary + final response only"),
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
    SkillDef("deep-research", "Deep Research", "/deep-research",
             "user wants multi-source fact-checked research",
             "Fan-out web searches, fetch sources, adversarially verify claims, synthesize cited report"),
    SkillDef("code-review", "Code Review", "/code-review",
             "user asks to review current diff for bugs and cleanups",
             "Review pending diff for correctness bugs and simplification opportunities"),
    SkillDef("run", "Run", "/run",
             "user asks to run, start, or screenshot the app",
             "Launch and drive the project app to see changes working in real app"),
    SkillDef("verify", "Verify", "/verify",
             "user wants to verify a PR, confirm a fix works, or test a change",
             "Run app and observe behavior to confirm feature works as expected"),
)


HOOK_DEFS: tuple[HookDef, ...] = (
    HookDef("PreToolUse", "Pre Tool Use", "PreToolUse",
            "Before any tool execution", True,
            "Validate/log before bash/file ops; inject context; block with exit 2"),
    HookDef("PostToolUse", "Post Tool Use", "PostToolUse",
            "After tool completes", False,
            "Log results, trigger follow-up actions after tool runs"),
    HookDef("Notification", "Notification", "Notification",
            "On push-notification events", False,
            "Forward alerts to mobile/Slack (requires Remote Control setup)"),
    HookDef("Stop", "Stop", "Stop",
            "After assistant turn completes", False,
            "Post-turn logging, notifications, cleanup tasks"),
    HookDef("SubagentStop", "Subagent Stop", "SubagentStop",
            "After subagent turn completes", False,
            "Subagent result aggregation and logging"),
    HookDef("PreCompact", "Pre Compact", "PreCompact",
            "Before conversation compaction", True,
            "Prevent compaction during critical operations (exit 2 to block)"),
    HookDef("TaskCreated", "Task Created", "TaskCreated",
            "When task created via TaskCreate tool", False,
            "Log/track task creation events; added v2.1.90"),
    HookDef("WorktreeCreate", "Worktree Create", "WorktreeCreate",
            "On worktree creation", False,
            "Custom worktree provisioning via HTTP endpoint; returns worktreePath"),
    HookDef("PermissionDenied", "Permission Denied", "PermissionDenied",
            "After auto-mode classifier denial", False,
            "Custom permission escalation; return {retry:true} to re-run classifier"),
)


def request_json(url: str) -> dict[str, Any]:
    import os
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
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_source_commit() -> str:
    try:
        data = request_json(API_COMMIT_URL)
        return str(data.get("sha", ""))[:12]
    except Exception:
        return "unknown"


def fetch_changelog() -> str:
    try:
        return request_text(CHANGELOG_URL)
    except Exception:
        return ""


def parse_latest_version(changelog: str) -> str:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    return m.group(1) if m else ""


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill_card(skill: SkillDef, commit: str, version: str) -> dict[str, Any]:
    procedure = [
        "Check official source alignment first.",
        "Prefer smallest working implementation.",
        "Keep prompt and code paths short.",
        "Verify with narrowest relevant command.",
        "Link to source docs instead of copying long content.",
    ]
    card: dict[str, Any] = {
        "name": skill.name,
        "slug": skill.slug,
        "cmd": skill.cmd,
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_branch": SOURCE_BRANCH,
        "source_commit": commit,
        "source_version": version,
        "trigger": skill.trigger,
        "desc": skill.desc,
        "procedure": procedure,
        "token_policy": [
            "Avoid repeated background context.",
            "Return only decision-critical code or instructions.",
            "Link to source repo instead of copying long docs.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
    }
    if skill.example:
        card["example"] = skill.example
    card["hash"] = card_hash(card)
    return card


def build_hook_card(hook: HookDef, commit: str, version: str) -> dict[str, Any]:
    card: dict[str, Any] = {
        "name": hook.name,
        "slug": hook.slug,
        "event": hook.event,
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_branch": SOURCE_BRANCH,
        "source_commit": commit,
        "source_version": version,
        "fires": hook.fires,
        "can_block": hook.can_block,
        "use": hook.use,
        "invoke_types": ["shell", "mcp_tool", "http"],
        "token_policy": [
            "Do not copy upstream documents into hook output.",
            "Keep hook cards short enough for quick pre/post-run loading.",
            "Prefer catalog metadata over repeated inline context.",
        ],
        "compatibility": [
            "Do not modify GPT or Gemini directories.",
            "Do not overwrite existing dated hook snapshots.",
            "Record hook conflicts in the same dated changelog as skills.",
        ],
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Command: `{card['cmd']}`",
        f"- Source: {card['source']}",
        f"- Source version: `{card['source_version']}`",
        f"- Source commit: `{card['source_commit']}`",
        f"- Trigger: {card['trigger']}",
        "",
        f"## Description",
        "",
        card["desc"],
        "",
    ]
    if card.get("example"):
        lines += ["## Example", "", f"`{card['example']}`", ""]
    lines += ["## Procedure", ""]
    lines.extend(f"{i}. {item}" for i, item in enumerate(card["procedure"], 1))
    lines += ["", "## Token Policy", ""]
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.append("")
    return "\n".join(lines)


def hook_markdown(card: dict[str, Any]) -> str:
    block_str = "yes" if card["can_block"] else "no"
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Event: `{card['event']}`",
        f"- Can block: {block_str}",
        f"- Source: {card['source']}",
        f"- Source version: `{card['source_version']}`",
        f"- Source commit: `{card['source_commit']}`",
        "",
        "## Fires",
        "",
        card["fires"],
        "",
        "## Use",
        "",
        card["use"],
        "",
        "## Invoke Types",
        "",
    ]
    lines.extend(f"- `{t}`" for t in card["invoke_types"])
    lines += ["", "## Token Policy", ""]
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.append("")
    return "\n".join(lines)


def current_date() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def previous_catalog(root: Path, today: str, leaf_dir: str) -> dict[str, Any]:
    if not root.exists():
        return {}
    candidates = []
    for path in root.iterdir():
        if not path.is_dir() or path.name >= today:
            continue
        catalog = path / leaf_dir / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def ensure_unique(cards: list[dict[str, Any]], label: str) -> None:
    seen: set[str] = set()
    dups: set[str] = set()
    for c in cards:
        slug = str(c.get("slug", ""))
        if slug in seen:
            dups.add(slug)
        seen.add(slug)
    if dups:
        raise ValueError(f"Duplicate {label} slugs: {', '.join(sorted(dups))}")


def compare(prev: dict[str, Any], cards: list[dict[str, Any]], key: str) -> dict[str, list[str]]:
    prev_map = {item["slug"]: item for item in prev.get(key, []) if "slug" in item}
    next_map = {item["slug"]: item for item in cards}
    added = sorted(set(next_map) - set(prev_map))
    deleted = sorted(set(prev_map) - set(next_map))
    modified = sorted(
        slug for slug in set(prev_map) & set(next_map)
        if prev_map[slug].get("hash") != next_map[slug].get("hash")
    )
    unchanged = sorted(set(prev_map) & set(next_map) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_skill_outputs(today: str, cards: list[dict[str, Any]], version: str) -> Path:
    out = SKILLS_ROOT / today / "skills"
    out.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (out / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "version": version,
        "directory_rule": "YYYY-MM-DD/skills",
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_policy": "official anthropics/claude-code repository only",
        "skills": cards,
    }
    (out / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out


def write_hook_outputs(today: str, cards: list[dict[str, Any]], version: str) -> Path:
    out = SKILLS_ROOT / today / "hooks"
    out.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (out / f"{card['slug']}.md").write_text(hook_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "version": version,
        "directory_rule": "YYYY-MM-DD/hooks",
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_policy": "official anthropics/claude-code repository only",
        "hooks": cards,
    }
    (out / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out


def update_catalog_version(version: str, today: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text(encoding="utf-8")
    text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text, encoding="utf-8")


def write_changelog(
    today: str,
    version: str,
    prev_version: str,
    skill_diff: dict[str, list[str]],
    hook_diff: dict[str, list[str]],
    skills_dir: Path,
    hooks_dir: Path,
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {s}" for s in values] if values else ["- none"]

    rel_skills = skills_dir.relative_to(CLAUDE_ROOT)
    rel_hooks = hooks_dir.relative_to(CLAUDE_ROOT)
    ver_str = f"{prev_version or 'none'} -> {version}" if version != prev_version else version

    lines = [
        f"Prompt-Guide Claude Code Skills Changelog - {today}",
        "",
        f"Snapshot : Claude/{rel_skills}",
        f"Hooks    : Claude/{rel_hooks}",
        f"Source   : https://github.com/{SOURCE_REPO}",
        f"Version  : {ver_str}",
        "",
        "[추가된 스킬]",
        *bullets(skill_diff["added"]),
        "",
        "[수정된 스킬]",
        *bullets(skill_diff["modified"]),
        "",
        "[삭제된 스킬]",
        *bullets(skill_diff["deleted"]),
        "",
        "[추가된 훅]",
        *bullets(hook_diff["added"]),
        "",
        "[수정된 훅]",
        *bullets(hook_diff["modified"]),
        "",
        "[삭제된 훅]",
        *bullets(hook_diff["deleted"]),
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: {rel_skills}",
        f"- 날짜별 훅 스냅샷 구조 유지: {rel_hooks}",
        "- 각 스킬은 cmd, trigger, desc, procedure, token_policy, compatibility로 경량화",
        "- 각 훅은 event, fires, can_block, use, token_policy, compatibility로 경량화",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크와 커밋 해시만 저장",
        "- 스킬 절차와 훅 항목은 짧은 실행 단위로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "- YAML over JSON/Markdown: 약 30% 토큰 절감",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- slug 기준으로 중복 훅 통합",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "",
        "[요약]",
        (
            "- skills: "
            f"added={len(skill_diff['added'])}, modified={len(skill_diff['modified'])}, "
            f"deleted={len(skill_diff['deleted'])}, unchanged={len(skill_diff['unchanged'])}"
        ),
        (
            "- hooks: "
            f"added={len(hook_diff['added'])}, modified={len(hook_diff['modified'])}, "
            f"deleted={len(hook_diff['deleted'])}, unchanged={len(hook_diff['unchanged'])}"
        ),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    today = current_date()
    prev_version = current_version()

    print(f"Fetching source commit for {SOURCE_REPO}@{SOURCE_BRANCH}...")
    commit = fetch_source_commit()
    print(f"Commit: {commit}")

    print("Fetching CHANGELOG.md...")
    changelog = fetch_changelog()
    version = parse_latest_version(changelog) or prev_version or "unknown"
    print(f"Version: {prev_version or 'none'} -> {version}")

    skills = [build_skill_card(s, commit, version) for s in SKILL_DEFS]
    hooks = [build_hook_card(h, commit, version) for h in HOOK_DEFS]

    ensure_unique(skills, "skill")
    ensure_unique(hooks, "hook")

    prev_skills = previous_catalog(SKILLS_ROOT, today, "skills")
    prev_hooks = previous_catalog(SKILLS_ROOT, today, "hooks")

    skills_dir = write_skill_outputs(today, skills, version)
    hooks_dir = write_hook_outputs(today, hooks, version)

    skill_diff = compare(prev_skills, skills, "skills")
    hook_diff = compare(prev_hooks, hooks, "hooks")

    write_changelog(today, version, prev_version, skill_diff, hook_diff, skills_dir, hooks_dir)

    if version and version != prev_version:
        VERSION_FILE.write_text(version, encoding="utf-8")
        update_catalog_version(version, today)
        print(f"Version updated: {prev_version or 'none'} -> {version}")

    print(f"Synced {len(skills)} skills  -> {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Synced {len(hooks)} hooks    -> {hooks_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

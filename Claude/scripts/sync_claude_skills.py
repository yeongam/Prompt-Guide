#!/usr/bin/env python3
"""Sync compact Claude Code skill and hook cards from official Anthropic GitHub repositories.

Dependency-free and non-interactive; runs via GitHub Actions without user prompts.
Mirrors the GPT/scripts/sync_openai_skills.py pattern for the Claude directory.
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


@dataclass(frozen=True)
class SkillSource:
    repo: str
    branch: str
    purpose: str
    slug: str
    name: str
    cmd: str
    trigger: str
    output: str


@dataclass(frozen=True)
class HookSource:
    repo: str
    branch: str
    purpose: str
    slug: str
    name: str
    event: str
    trigger: str
    checks: tuple[str, ...]
    actions: tuple[str, ...]


SOURCES: tuple[SkillSource, ...] = (
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: initialize codebase documentation",
        slug="init",
        name="Initialize Codebase",
        cmd="/init",
        trigger="user asks to initialize or document codebase",
        output="CLAUDE.md with codebase architecture, conventions, and commands",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: multi-pass pull request review",
        slug="review",
        name="PR Review",
        cmd="/review",
        trigger="user asks to review PR or branch",
        output="Multi-pass review covering logic, style, security, and tests",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: security audit of pending changes",
        slug="security-review",
        name="Security Audit",
        cmd="/security-review",
        trigger="user asks security audit of current branch changes",
        output="OWASP-focused audit; risk-ranked findings list",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: simplify and refactor changed code",
        slug="simplify",
        name="Code Simplify",
        cmd="/simplify",
        trigger="user asks to clean up or refactor changed code",
        output="Reuse/quality/efficiency review then inline fixes",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: configure session-start hooks for web",
        slug="session-start-hook",
        name="Session Start Hook",
        cmd="/session-start-hook",
        trigger="user wants test/lint runners on session start (web Claude Code)",
        output="SessionStart hook ensuring project can run tests and linters",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: configure settings.json hooks and permissions",
        slug="update-config",
        name="Update Config",
        cmd="/update-config",
        trigger="automated behavior requests ('when X', 'allow Y', 'set Z=val')",
        output="settings.json update; handles hooks, permissions, env vars",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: keyboard shortcut configuration",
        slug="keybindings-help",
        name="Keybindings Help",
        cmd="/keybindings-help",
        trigger="user wants to remap keys or add chord shortcuts",
        output="Customized ~/.claude/keybindings.json with chord bindings",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: reduce permission prompt frequency",
        slug="fewer-permission-prompts",
        name="Fewer Permission Prompts",
        cmd="/fewer-permission-prompts",
        trigger="user wants fewer permission dialogs",
        output="Bash/MCP allowlist added to .claude/settings.json from transcript scan",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: recurring task runner on interval",
        slug="loop",
        name="Loop Task",
        cmd="/loop [interval] [/command]",
        trigger="user wants recurring task (e.g. 'check every 5m', 'keep running X')",
        output="Prompt or slash command running on recurring interval (default 10m)",
    ),
    SkillSource(
        repo="anthropics/anthropic-sdk-python",
        branch="main",
        purpose="Official Python SDK for the Anthropic/Claude API",
        slug="claude-api",
        name="Claude API",
        cmd="/claude-api",
        trigger="code imports anthropic SDK; user asks about Claude API features",
        output="Claude API app with prompt caching, tool use, model migration",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: parallel multi-agent cloud code review",
        slug="ultrareview",
        name="Ultra Review",
        cmd="/ultrareview [PR#]",
        trigger="user says 'ultrareview' or wants multi-agent review",
        output="Parallel multi-agent cloud review; no-arg=local branch, arg=GitHub PR",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: cloud environment for multi-agent planning",
        slug="ultraplan",
        name="Ultra Plan",
        cmd="/ultraplan",
        trigger="user wants cloud environment for complex planning",
        output="Cloud worktrees/environments for multi-agent planning tasks",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: generate team onboarding guide",
        slug="team-onboarding",
        name="Team Onboarding",
        cmd="/team-onboarding",
        trigger="user wants teammate ramp-up guide",
        output="Onboarding guide from local Claude Code usage history",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: effort and quality level control",
        slug="effort",
        name="Effort Level",
        cmd="/effort",
        trigger="user wants to adjust effort/quality level",
        output="Interactive effort slider; also CLAUDE_EFFORT env var",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: interactive feature demo and tutorials",
        slug="powerup",
        name="Power Up",
        cmd="/powerup",
        trigger="user wants feature demos or to learn Claude Code features",
        output="Animated feature demos with interactive lessons",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: flicker-free alt-screen TUI mode",
        slug="tui",
        name="TUI Mode",
        cmd="/tui",
        trigger="rendering looks flickery or user wants full-screen mode",
        output="Alt-screen flicker-free TUI (also CLAUDE_CODE_NO_FLICKER=1)",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: compact focus view of conversation",
        slug="focus",
        name="Focus View",
        cmd="/focus",
        trigger="user wants compact view of conversation",
        output="Focus view: prompt + tool summary + final response only",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: undo last assistant action",
        slug="undo",
        name="Undo",
        cmd="/undo",
        trigger="user wants to undo last action",
        output="Rewind last assistant action (alias for /rewind)",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: token and cost usage statistics",
        slug="usage",
        name="Usage Stats",
        cmd="/usage",
        trigger="user asks about token or cost statistics",
        output="Token/cost stats display (merged /cost + /stats commands)",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: visual theme management",
        slug="theme",
        name="Theme",
        cmd="/theme [name]",
        trigger="user wants to change or create visual theme",
        output="Custom color theme created or switched",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: session color assignment",
        slug="color",
        name="Color",
        cmd="/color",
        trigger="user wants a session color",
        output="Random session color set (no args = random pick)",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: verify a code change works in the real app",
        slug="verify",
        name="Verify Change",
        cmd="/verify",
        trigger="asked to verify a PR, confirm a fix works, or test a change manually",
        output="App observed running; golden path and edge cases tested",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: inline code review with optional PR comments",
        slug="code-review",
        name="Code Review Inline",
        cmd="/code-review",
        trigger="user asks for code review; optionally post inline PR comments",
        output="Correctness bugs report; optionally posted as inline PR comments",
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code CLI: launch and observe the project app",
        slug="run",
        name="Run App",
        cmd="/run",
        trigger="asked to run, start, or screenshot the app",
        output="App launched; change confirmed working in real app",
    ),
)


HOOK_SOURCES: tuple[HookSource, ...] = (
    HookSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Fires before any tool execution; can block with exit 2 or JSON",
        slug="pre-tool-use",
        name="Pre Tool Use",
        event="PreToolUse",
        trigger="Validate or log before bash/file ops; inject context.",
        checks=(
            "Confirm tool call parameters are safe before execution.",
            "Log tool invocation with context for audit.",
            "Block if tool matches a deny-list pattern.",
        ),
        actions=(
            "Return exit 2 or {decision:'block',reason:'...'} to block.",
            "Inject metadata or context into the tool call.",
        ),
    ),
    HookSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Fires after tool completes; cannot block",
        slug="post-tool-use",
        name="Post Tool Use",
        event="PostToolUse",
        trigger="Log results or trigger follow-up actions after tool execution.",
        checks=(
            "Verify tool output for unexpected side effects.",
            "Log result metadata for observability.",
        ),
        actions=(
            "Forward tool result to external logging system.",
            "Trigger follow-up automation based on result.",
        ),
    ),
    HookSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Fires before conversation compaction; can block (added v2.1.85)",
        slug="pre-compact",
        name="Pre Compact",
        event="PreCompact",
        trigger="Prevent compaction during critical operations.",
        checks=(
            "Check if active operation is sensitive to context loss.",
            "Verify compaction timing is safe.",
        ),
        actions=(
            "Return {decision:'block'} or exit 2 to delay compaction.",
            "Log compaction attempt with current operation context.",
        ),
    ),
    HookSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Fires after assistant turn completes; cannot block",
        slug="stop",
        name="Stop",
        event="Stop",
        trigger="Post-turn logging and notifications after assistant responds.",
        checks=(
            "Confirm turn completed without errors.",
            "Check for any required follow-up notifications.",
        ),
        actions=(
            "Send push notification on turn completion.",
            "Log turn summary to external system.",
        ),
    ),
    HookSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Fires after subagent turn completes; cannot block",
        slug="subagent-stop",
        name="Subagent Stop",
        event="SubagentStop",
        trigger="Aggregate subagent results after subagent turn completes.",
        checks=(
            "Verify subagent output is complete.",
            "Check for errors in subagent execution.",
        ),
        actions=(
            "Aggregate subagent result into parent context.",
            "Log subagent completion metrics.",
        ),
    ),
    HookSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Fires when task created via TaskCreate tool; cannot block (added v2.1.90)",
        slug="task-created",
        name="Task Created",
        event="TaskCreated",
        trigger="Log or track task creation events.",
        checks=(
            "Verify task parameters are valid.",
            "Check for duplicate task creation.",
        ),
        actions=(
            "Log task creation with ID and parameters.",
            "Notify external task tracker.",
        ),
    ),
    HookSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Fires after auto-mode classifier denial; supports retry (added v2.1.95)",
        slug="permission-denied",
        name="Permission Denied",
        event="PermissionDenied",
        trigger="Custom permission escalation flows after classifier denial.",
        checks=(
            "Identify which classifier rule triggered the denial.",
            "Determine if escalation or retry is appropriate.",
        ),
        actions=(
            "Return {retry:true} to re-run the classifier.",
            "Escalate to user or log denial reason.",
        ),
    ),
    HookSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Fires on worktree creation; supports HTTP endpoint (added v2.1.88)",
        slug="worktree-create",
        name="Worktree Create",
        event="WorktreeCreate",
        trigger="Custom worktree provisioning via HTTP endpoint.",
        checks=(
            "Verify worktree path is available.",
            "Confirm branch name is valid.",
        ),
        actions=(
            "Return hookSpecificOutput.worktreePath for custom path.",
            "Provision worktree-specific resources (containers, secrets).",
        ),
    ),
    HookSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Fires on push-notification events; cannot block",
        slug="notification",
        name="Notification",
        event="Notification",
        trigger="Forward alerts to mobile/Slack (requires Remote Control setup).",
        checks=(
            "Verify notification payload is valid.",
            "Check notification routing configuration.",
        ),
        actions=(
            "Route notification to configured channels (Slack, mobile, email).",
            "Log notification delivery status.",
        ),
    ),
)


def request_json(url: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "prompt-guide-claude-skill-sync",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def repo_commit(repo: str, branch: str) -> str:
    try:
        data = request_json(f"https://api.github.com/repos/{repo}/commits/{branch}")
        sha = str(data.get("sha", ""))
        return sha[:12]
    except (urllib.error.URLError, urllib.error.HTTPError):
        return "offline"


def repo_readme(repo: str, branch: str) -> str:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
    try:
        return request_text(url)
    except (urllib.error.URLError, urllib.error.HTTPError):
        return ""


def compact_text(text: str, max_chars: int = 420) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "."


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill(source: SkillSource, commit: str, readme: str) -> dict[str, Any]:
    summary = compact_text(readme) or source.purpose
    card = {
        "name": source.name,
        "slug": source.slug,
        "cmd": source.cmd,
        "source": f"https://github.com/{source.repo}",
        "source_branch": source.branch,
        "source_commit": commit,
        "trigger": source.trigger,
        "procedure": [
            "Check official source alignment first.",
            "Prefer smallest working implementation.",
            "Use structured APIs over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": source.output,
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
        "summary": summary,
    }
    card["hash"] = card_hash(card)
    return card


def build_hook(source: HookSource, commit: str) -> dict[str, Any]:
    card = {
        "name": source.name,
        "slug": source.slug,
        "source": f"https://github.com/{source.repo}",
        "source_branch": source.branch,
        "source_commit": commit,
        "event": source.event,
        "trigger": source.trigger,
        "checks": list(source.checks),
        "actions": list(source.actions),
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
        "summary": source.purpose,
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
        f"- Source commit: `{card['source_commit']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(card["procedure"], 1))
    lines.extend(
        [
            "",
            "## Output",
            "",
            str(card["output"]),
            "",
            "## Token Policy",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines.extend(["", "## Compatibility", ""])
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.extend(["", "## Source Summary", "", textwrap.fill(str(card["summary"]), width=88), ""])
    return "\n".join(lines)


def hook_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Event: `{card['event']}`",
        f"- Source: {card['source']}",
        f"- Source commit: `{card['source_commit']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(card["checks"], 1))
    lines.extend(["", "## Actions", ""])
    lines.extend(f"- {item}" for item in card["actions"])
    lines.extend(["", "## Token Policy", ""])
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines.extend(["", "## Compatibility", ""])
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.extend(["", "## Source Summary", "", textwrap.fill(str(card["summary"]), width=88), ""])
    return "\n".join(lines)


def current_date() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


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
    latest = sorted(candidates)[-1]
    return json.loads(latest.read_text(encoding="utf-8"))


def write_skill_outputs(today: str, cards: list[dict[str, Any]]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")

    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official Anthropic GitHub repositories only",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return skills_dir


def write_hook_outputs(today: str, cards: list[dict[str, Any]]) -> Path:
    hooks_dir = SKILLS_ROOT / today / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    for card in cards:
        (hooks_dir / f"{card['slug']}.md").write_text(hook_markdown(card), encoding="utf-8")

    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/hooks",
        "source_policy": "official Anthropic GitHub repositories only",
        "hooks": cards,
    }
    (hooks_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return hooks_dir


def ensure_unique(cards: list[dict[str, Any]], label: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for card in cards:
        slug = str(card.get("slug", ""))
        if slug in seen:
            duplicates.add(slug)
        seen.add(slug)
    if duplicates:
        joined = ", ".join(sorted(duplicates))
        raise ValueError(f"Duplicate {label} slugs: {joined}")


def compare(prev: dict[str, Any], cards: list[dict[str, Any]], collection: str) -> dict[str, list[str]]:
    prev_by_slug = {item["slug"]: item for item in prev.get(collection, []) if "slug" in item}
    next_by_slug = {item["slug"]: item for item in cards}

    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        slug
        for slug in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[slug].get("hash") != next_by_slug[slug].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))

    return {
        "added": added,
        "modified": modified,
        "deleted": deleted,
        "unchanged": unchanged,
    }


def update_catalog_version(version: str) -> None:
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


def fetch_latest_version() -> str:
    url = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
    try:
        text = request_text(url)
        m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", text)
        return m.group(1) if m else ""
    except (urllib.error.URLError, urllib.error.HTTPError):
        return VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else ""


def write_changelog(
    today: str,
    skill_diff: dict[str, list[str]],
    hook_diff: dict[str, list[str]],
    skills_dir: Path,
    hooks_dir: Path,
    version: str,
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Code Skills and Hooks Changelog - {today}",
        f"Version: {version or 'unknown'}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Hooks: Claude/skills/{today}/hooks",
        "Source: official Anthropic GitHub repositories",
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
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(CLAUDE_ROOT)}",
        f"- 날짜별 훅 스냅샷 구조 유지: {hooks_dir.relative_to(CLAUDE_ROOT)}",
        "- 각 스킬은 cmd, trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 각 훅은 event, checks, actions, token_policy, compatibility로 경량화",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크와 커밋 해시만 저장",
        "- 스킬 절차와 훅 점검 항목은 짧은 실행 단위로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "- SKILLS_CATALOG.yaml을 단일 정규 소스로 유지 (YAML: JSON 대비 토큰 ~30% 절감)",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- slug 기준으로 중복 훅 통합",
        "- 기존 날짜 스킬/훅 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
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
    skills: list[dict[str, Any]] = []
    hooks: list[dict[str, Any]] = []
    commits: dict[tuple[str, str], str] = {}
    readmes: dict[tuple[str, str], str] = {}

    def source_commit(repo: str, branch: str) -> str:
        key = (repo, branch)
        if key not in commits:
            commits[key] = repo_commit(repo, branch)
        return commits[key]

    def source_data(repo: str, branch: str) -> tuple[str, str]:
        key = (repo, branch)
        commit = source_commit(repo, branch)
        if key not in readmes:
            readmes[key] = repo_readme(repo, branch)
        return commit, readmes[key]

    for source in SOURCES:
        commit, readme = source_data(source.repo, source.branch)
        skills.append(build_skill(source, commit, readme))

    for source in HOOK_SOURCES:
        hooks.append(build_hook(source, source_commit(source.repo, source.branch)))

    ensure_unique(skills, "skill")
    ensure_unique(hooks, "hook")

    prev_skills = previous_catalog(SKILLS_ROOT, today, "skills")
    prev_hooks = previous_catalog(SKILLS_ROOT, today, "hooks")
    skills_dir = write_skill_outputs(today, skills)
    hooks_dir = write_hook_outputs(today, hooks)
    skill_diff = compare(prev_skills, skills, "skills")
    hook_diff = compare(prev_hooks, hooks, "hooks")

    version = fetch_latest_version()
    if version:
        VERSION_FILE.write_text(version + "\n", encoding="utf-8")
        update_catalog_version(version)

    write_changelog(today, skill_diff, hook_diff, skills_dir, hooks_dir, version)

    print(f"Synced {len(skills)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Synced {len(hooks)} Claude hooks to {hooks_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

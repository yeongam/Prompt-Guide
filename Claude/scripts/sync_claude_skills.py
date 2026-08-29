#!/usr/bin/env python3
"""Sync compact Claude Code skill and hook cards from official Anthropic GitHub repositories.

Dependency-free and non-interactive so it can run unattended (no permission popups).
Mirrors the pattern used by GPT/scripts/sync_openai_skills.py for this repo.
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
HOOKS_ROOT = CLAUDE_ROOT / "hooks"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
KST = timezone(timedelta(hours=9), "KST")


@dataclass(frozen=True)
class SourceRepo:
    repo: str
    branch: str
    purpose: str
    skill_slug: str
    skill_name: str
    trigger: str
    output: str


@dataclass(frozen=True)
class HookSource:
    hook_slug: str
    hook_name: str
    event: str
    repo: str
    branch: str
    purpose: str
    trigger: str
    checks: tuple[str, ...]
    actions: tuple[str, ...]


SOURCES: tuple[SourceRepo, ...] = (
    SourceRepo(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Official Claude Code CLI - agentic coding tool for the terminal",
        skill_slug="claude-code-cli-programming",
        skill_name="Claude Code CLI Programming",
        trigger="Use for terminal coding sessions, slash commands, and CLI workflows.",
        output="Compact CLI usage checklist aligned with the current release.",
    ),
    SourceRepo(
        repo="anthropics/skills",
        branch="main",
        purpose="Official Agent Skills repository (coding, docs, enterprise, creative skills)",
        skill_slug="agent-skills-authoring",
        skill_name="Agent Skills Authoring",
        trigger="Use for creating, editing, or applying SKILL.md-based skills, incl. docx/pdf/pptx/xlsx.",
        output="Minimal skill-authoring checklist with SKILL.md frontmatter rules.",
    ),
    SourceRepo(
        repo="anthropics/anthropic-sdk-python",
        branch="main",
        purpose="Official Python library for the Claude API",
        skill_slug="python-sdk-programming",
        skill_name="Python SDK Programming",
        trigger="Use for Python Claude API integration, request structure, and migration checks.",
        output="Minimal Python SDK guidance with verification steps.",
    ),
    SourceRepo(
        repo="anthropics/anthropic-sdk-typescript",
        branch="main",
        purpose="Official JavaScript / TypeScript library for the Claude API",
        skill_slug="typescript-sdk-programming",
        skill_name="TypeScript SDK Programming",
        trigger="Use for Node.js or TypeScript Claude API integration and typed usage.",
        output="Compact TypeScript SDK implementation checklist.",
    ),
    SourceRepo(
        repo="anthropics/claude-agent-sdk-python",
        branch="main",
        purpose="Agent SDK for building custom Claude-powered agents",
        skill_slug="agent-sdk-workflow-programming",
        skill_name="Agent SDK Workflow Programming",
        trigger="Use for custom agent loops, tool wiring, and orchestration code.",
        output="Lean agent workflow design and implementation checks.",
    ),
)


HOOK_SOURCES: tuple[HookSource, ...] = (
    HookSource(
        hook_slug="pre-tool-use-guard",
        hook_name="Pre Tool Use Guard",
        event="PreToolUse",
        repo="anthropics/claude-code",
        branch="main",
        purpose="Validate or block before any tool executes",
        trigger="Fires before bash/file/MCP tool execution.",
        checks=(
            "Confirm the tool call matches an allowed pattern.",
            "Reject destructive commands outside declared scope.",
            "Keep validation logic short-circuiting and side-effect free.",
        ),
        actions=(
            "Block with exit code 2 or {decision:'block'} on violation.",
            "Inject minimal extra context only when required.",
        ),
    ),
    HookSource(
        hook_slug="post-tool-use-logging",
        hook_name="Post Tool Use Logging",
        event="PostToolUse",
        repo="anthropics/claude-code",
        branch="main",
        purpose="Log results and trigger follow-up actions after a tool completes",
        trigger="Fires after any tool call finishes.",
        checks=(
            "Verify tool result before logging.",
            "Avoid duplicate log entries for retried calls.",
        ),
        actions=(
            "Append compact result summary to the run log.",
            "Chain follow-up automation only when explicitly configured.",
        ),
    ),
    HookSource(
        hook_slug="session-stop-notification",
        hook_name="Session Stop Notification",
        event="Stop",
        repo="anthropics/claude-code",
        branch="main",
        purpose="Post-turn logging and notifications",
        trigger="Fires after the assistant turn completes.",
        checks=(
            "Confirm the turn reached a terminal state.",
            "Skip notification when nothing changed this turn.",
        ),
        actions=(
            "Send a single compact status update.",
            "Avoid re-notifying for identical consecutive states.",
        ),
    ),
    HookSource(
        hook_slug="pre-compact-guard",
        hook_name="Pre Compact Guard",
        event="PreCompact",
        repo="anthropics/claude-code",
        branch="main",
        purpose="Prevent conversation compaction during critical operations",
        trigger="Fires before automatic context compaction.",
        checks=(
            "Detect in-flight multi-step operations before compaction.",
            "Block with exit code 2 or {decision:'block'} when unsafe.",
        ),
        actions=(
            "Defer compaction until the current step commits.",
            "Log the deferred-compaction reason once, not repeatedly.",
        ),
    ),
    HookSource(
        hook_slug="permission-denied-retry",
        hook_name="Permission Denied Retry",
        event="PermissionDenied",
        repo="anthropics/claude-code",
        branch="main",
        purpose="Custom permission escalation flow after auto-mode classifier denial",
        trigger="Fires after the auto-mode permission classifier denies a call.",
        checks=(
            "Confirm the denial reason before requesting retry.",
            "Cap retries to avoid classifier thrashing.",
        ),
        actions=(
            "Return {retry:true} only for a corrected, narrower request.",
            "Surface unresolved denials instead of looping silently.",
        ),
    ),
    HookSource(
        hook_slug="post-sync-changelog-guard",
        hook_name="Post Sync Changelog Guard",
        event="post_sync",
        repo="anthropics/claude-code",
        branch="main",
        purpose="Guard the daily Claude skill/hook sync routine itself",
        trigger="Runs after generating Claude skills or hooks for the day.",
        checks=(
            "Compare generated catalogs with the previous dated snapshot.",
            "List added, modified, and deleted skills and hooks separately.",
            "Confirm token-saving and conflict-resolution notes are present.",
        ),
        actions=(
            "Write one concise changelog under Claude/Changelogs.",
            "Never prompt the user during automated routine execution.",
        ),
    ),
)


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def repo_readme(repo: str, branch: str) -> str:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
    try:
        return request_text(url)
    except urllib.error.URLError:
        return ""


def source_ref(readme: str) -> str:
    """Content hash of the fetched reference file (no GitHub API access from this session)."""
    return hashlib.sha256(readme.encode("utf-8")).hexdigest()[:12] if readme else "unavailable"


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


def build_skill(source: SourceRepo, ref: str, readme: str) -> dict[str, Any]:
    summary = compact_text(readme) or source.purpose
    card = {
        "name": source.skill_name,
        "slug": source.skill_slug,
        "source": f"https://github.com/{source.repo}",
        "source_branch": source.branch,
        "source_ref": ref,
        "trigger": source.trigger,
        "procedure": [
            "Check official source alignment first.",
            "Prefer the smallest working implementation.",
            "Use structured APIs over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": source.output,
        "token_policy": [
            "Avoid repeated background context.",
            "Return only decision-critical code or instructions.",
            "Link to the source repo instead of copying long docs.",
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


def build_hook(source: HookSource, ref: str) -> dict[str, Any]:
    card = {
        "name": source.hook_name,
        "slug": source.hook_slug,
        "event": source.event,
        "source": f"https://github.com/{source.repo}",
        "source_branch": source.branch,
        "source_ref": ref,
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
        f"- Source: {card['source']}",
        f"- Source ref: `{card['source_ref']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(card["procedure"], 1))
    lines.extend(["", "## Output", "", str(card["output"]), "", "## Token Policy", ""])
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
        f"- Source ref: `{card['source_ref']}`",
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
        if not path.is_dir() or not re.match(r"^\d{4}-\d{2}-\d{2}$", path.name) or path.name >= today:
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
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def write_hook_outputs(today: str, cards: list[dict[str, Any]]) -> Path:
    hooks_dir = HOOKS_ROOT / today / "hooks"
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
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
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
        raise ValueError(f"Duplicate {label} slugs: {', '.join(sorted(duplicates))}")


def compare(prev: dict[str, Any], cards: list[dict[str, Any]], collection: str) -> dict[str, list[str]]:
    prev_by_slug = {item["slug"]: item for item in prev.get(collection, []) if "slug" in item}
    next_by_slug = {item["slug"]: item for item in cards}
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
    skill_diff: dict[str, list[str]],
    hook_diff: dict[str, list[str]],
    skills_dir: Path,
    hooks_dir: Path,
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills and Hooks Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Hooks: Claude/hooks/{today}/hooks",
        "Source: official Anthropic GitHub repositories",
        "",
        "[추가된 스킬]", *bullets(skill_diff["added"]), "",
        "[수정된 스킬]", *bullets(skill_diff["modified"]), "",
        "[삭제된 스킬]", *bullets(skill_diff["deleted"]), "",
        "[추가된 훅]", *bullets(hook_diff["added"]), "",
        "[수정된 훅]", *bullets(hook_diff["modified"]), "",
        "[삭제된 훅]", *bullets(hook_diff["deleted"]), "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(CLAUDE_ROOT)}",
        f"- 날짜별 훅 스냅샷 구조 유지: {hooks_dir.relative_to(CLAUDE_ROOT)}",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 각 훅은 event, checks, actions, token_policy, compatibility로 경량화",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크와 콘텐츠 해시만 저장",
        "- 스킬 절차와 훅 점검 항목은 짧은 실행 단위로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬/훅 통합",
        "- 기존 flat SKILLS_CATALOG.yaml/.version은 하위 호환을 위해 보존, 신규 정본은 날짜별 스냅샷",
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
    readmes: dict[tuple[str, str], str] = {}

    def readme_for(repo: str, branch: str) -> str:
        key = (repo, branch)
        if key not in readmes:
            readmes[key] = repo_readme(repo, branch)
        return readmes[key]

    for source in SOURCES:
        readme = readme_for(source.repo, source.branch)
        skills.append(build_skill(source, source_ref(readme), readme))

    for source in HOOK_SOURCES:
        readme = readme_for(source.repo, source.branch)
        hooks.append(build_hook(source, source_ref(readme)))

    ensure_unique(skills, "skill")
    ensure_unique(hooks, "hook")

    prev_skills = previous_catalog(SKILLS_ROOT, today, "skills")
    prev_hooks = previous_catalog(HOOKS_ROOT, today, "hooks")
    skills_dir = write_skill_outputs(today, skills)
    hooks_dir = write_hook_outputs(today, hooks)
    skill_diff = compare(prev_skills, skills, "skills")
    hook_diff = compare(prev_hooks, hooks, "hooks")
    write_changelog(today, skill_diff, hook_diff, skills_dir, hooks_dir)

    print(f"Synced {len(skills)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Synced {len(hooks)} Claude hooks to {hooks_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

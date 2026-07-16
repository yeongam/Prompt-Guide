#!/usr/bin/env python3
"""Sync compact Claude skill and hook cards from official Anthropic GitHub repositories.

The script is intentionally dependency-free and non-interactive so it can run in
GitHub Actions without prompts. Mirrors GPT/scripts/sync_openai_skills.py.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
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
    repo: str
    branch: str
    purpose: str
    hook_slug: str
    hook_name: str
    event: str
    trigger: str
    checks: tuple[str, ...]
    actions: tuple[str, ...]


SOURCES: tuple[SourceRepo, ...] = (
    SourceRepo(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Official Claude Code CLI coding agent",
        skill_slug="claude-code-coding",
        skill_name="Claude Code Coding",
        trigger="Use for implementing or debugging work done through the Claude Code CLI.",
        output="Small code-oriented checklist with official-example alignment.",
    ),
    SourceRepo(
        repo="anthropics/anthropic-sdk-python",
        branch="main",
        purpose="Official Python library for the Anthropic API",
        skill_slug="python-sdk-programming",
        skill_name="Python SDK Programming",
        trigger="Use for Python SDK integration, request structure, and migration checks.",
        output="Minimal Python SDK guidance with verification steps.",
    ),
    SourceRepo(
        repo="anthropics/anthropic-sdk-typescript",
        branch="main",
        purpose="Official JavaScript / TypeScript library for the Anthropic API",
        skill_slug="typescript-sdk-programming",
        skill_name="TypeScript SDK Programming",
        trigger="Use for Node.js or TypeScript SDK integration and typed API work.",
        output="Compact TypeScript SDK implementation checklist.",
    ),
    SourceRepo(
        repo="anthropics/claude-agent-sdk-python",
        branch="main",
        purpose="Framework for building custom Claude agents",
        skill_slug="agents-workflow-programming",
        skill_name="Agents Workflow Programming",
        trigger="Use for agent workflows, tool use, and orchestration code.",
        output="Lean agent workflow design and implementation checks.",
    ),
    SourceRepo(
        repo="anthropics/claude-cookbooks",
        branch="main",
        purpose="Documentation and cookbook examples for Claude API workflows",
        skill_slug="documentation-maintenance",
        skill_name="Documentation Maintenance",
        trigger="Use for updating docs, examples, prompts, and developer guides.",
        output="Concise documentation update checklist with source traceability.",
    ),
)


HOOK_SOURCES: tuple[HookSource, ...] = (
    HookSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Official Claude Code CLI coding agent",
        hook_slug="pre-sync-source-alignment",
        hook_name="Pre Sync Source Alignment",
        event="pre_sync",
        trigger="Run before generating Claude skills or hooks.",
        checks=(
            "Resolve the latest official Anthropic source commit.",
            "Reject unofficial source material for generated artifacts.",
            "Confirm skill and hook slugs are unique before writing files.",
        ),
        actions=(
            "Record source URL, branch, and commit in each generated card.",
            "Use source summaries instead of copying long upstream content.",
        ),
    ),
    HookSource(
        repo="anthropics/anthropic-sdk-python",
        branch="main",
        purpose="Official Python library for the Anthropic API",
        hook_slug="python-sdk-compatibility-check",
        hook_name="Python SDK Compatibility Check",
        event="pre_apply",
        trigger="Run before applying Python SDK guidance or examples.",
        checks=(
            "Verify the Python SDK source commit used by the routine.",
            "Prefer current SDK request shapes over stale snippets.",
            "Keep migration notes compact and version-aware.",
        ),
        actions=(
            "Attach commit evidence to Python SDK skill output.",
            "Flag incompatible examples in the changelog conflict section.",
        ),
    ),
    HookSource(
        repo="anthropics/anthropic-sdk-typescript",
        branch="main",
        purpose="Official JavaScript / TypeScript library for the Anthropic API",
        hook_slug="typescript-sdk-compatibility-check",
        hook_name="TypeScript SDK Compatibility Check",
        event="pre_apply",
        trigger="Run before applying TypeScript SDK guidance or examples.",
        checks=(
            "Verify the TypeScript SDK source commit used by the routine.",
            "Keep generated guidance aligned with typed SDK usage.",
            "Avoid duplicating Python-specific patterns in TypeScript output.",
        ),
        actions=(
            "Attach commit evidence to TypeScript SDK skill output.",
            "Flag cross-language conflicts in the changelog conflict section.",
        ),
    ),
    HookSource(
        repo="anthropics/claude-agent-sdk-python",
        branch="main",
        purpose="Framework for building custom Claude agents",
        hook_slug="agent-workflow-guard",
        hook_name="Agent Workflow Guard",
        event="post_apply",
        trigger="Run after applying agent workflow guidance.",
        checks=(
            "Confirm tools and orchestration guidance stay separated.",
            "Prefer minimal runnable workflow patterns.",
            "Preserve existing Claude skill behavior when adding agent guidance.",
        ),
        actions=(
            "Record agent workflow conflicts in the changelog.",
            "Keep agent guidance short enough for fast reuse.",
        ),
    ),
    HookSource(
        repo="anthropics/claude-cookbooks",
        branch="main",
        purpose="Documentation and cookbook examples for Claude API workflows",
        hook_slug="post-sync-changelog-guard",
        hook_name="Post Sync Changelog Guard",
        event="post_sync",
        trigger="Run after Claude skills and hooks are generated.",
        checks=(
            "Compare generated catalogs with the previous dated snapshot.",
            "List added, modified, and deleted skills and hooks separately.",
            "Confirm token-saving and conflict-resolution notes are present.",
        ),
        actions=(
            "Write one concise changelog under Claude/Changelogs.",
            "Avoid prompting the user during automated routine execution.",
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
        if sha:
            return sha[:12]
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError):
        pass
    try:
        out = subprocess.run(
            ["git", "ls-remote", f"https://github.com/{repo}.git", branch],
            capture_output=True, text=True, timeout=30, check=True,
        )
        sha = out.stdout.split()[0] if out.stdout.strip() else ""
        return sha[:12]
    except (subprocess.SubprocessError, IndexError, OSError):
        return "unknown"


def repo_readme(repo: str, branch: str) -> str:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
    try:
        return request_text(url)
    except urllib.error.URLError:
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


def build_skill(source: SourceRepo, commit: str, readme: str) -> dict[str, Any]:
    summary = compact_text(readme) or source.purpose
    card = {
        "name": source.skill_name,
        "slug": source.skill_slug,
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
        "name": source.hook_name,
        "slug": source.hook_slug,
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
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 각 훅은 event, checks, actions, token_policy, compatibility로 경량화",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크와 커밋 해시만 저장",
        "- 스킬 절차와 훅 점검 항목은 짧은 실행 단위로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
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

#!/usr/bin/env python3
"""Bootstrap initial Claude skill snapshot without network access.

Used once to seed the first dated snapshot. Daily GitHub Actions runs
use sync_claude_skills.py with real API commits.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
HOOKS_ROOT = CLAUDE_ROOT / "hooks"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
KST = timezone(timedelta(hours=9), "KST")

BOOTSTRAP_COMMIT = "bootstrap-2026-06-13"

INITIAL_SKILLS = [
    {
        "name": "Claude Code CLI",
        "slug": "claude-code-cli",
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "trigger": "Use when implementing or extending Claude Code slash commands, hooks, or CLI features.",
        "procedure": [
            "Check official Anthropic source alignment first.",
            "Prefer smallest working implementation.",
            "Use structured APIs over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": "Compact Claude Code feature checklist with official-source alignment.",
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
        "summary": "Claude Code CLI — the official agentic coding assistant by Anthropic.",
    },
    {
        "name": "Anthropic Python SDK",
        "slug": "anthropic-python-sdk",
        "source": "https://github.com/anthropics/anthropic-sdk-python",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "trigger": "Use for Python-based Claude API integration, streaming, tool use, and migration checks.",
        "procedure": [
            "Check official Anthropic source alignment first.",
            "Prefer smallest working implementation.",
            "Use structured APIs over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": "Minimal Python SDK guidance with verification steps.",
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
        "summary": "Official Python SDK for the Anthropic (Claude) API.",
    },
    {
        "name": "Anthropic TypeScript SDK",
        "slug": "anthropic-typescript-sdk",
        "source": "https://github.com/anthropics/anthropic-sdk-javascript",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "trigger": "Use for Node.js or TypeScript Claude API integration and typed SDK work.",
        "procedure": [
            "Check official Anthropic source alignment first.",
            "Prefer smallest working implementation.",
            "Use structured APIs over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": "Compact TypeScript SDK implementation checklist.",
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
        "summary": "Official TypeScript/JavaScript SDK for the Anthropic (Claude) API.",
    },
    {
        "name": "Claude Code GitHub Action",
        "slug": "claude-code-action",
        "source": "https://github.com/anthropics/claude-code-action",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "trigger": "Use when wiring Claude Code into CI/CD pipelines or GitHub Actions workflows.",
        "procedure": [
            "Check official Anthropic source alignment first.",
            "Prefer smallest working implementation.",
            "Use structured APIs over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": "Lean GitHub Actions integration checklist with PR/issue automation notes.",
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
        "summary": "GitHub Actions integration for Claude Code — automate PR review and issue triage.",
    },
    {
        "name": "MCP Server Integration",
        "slug": "mcp-integration",
        "source": "https://github.com/anthropics/model-context-protocol",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "trigger": "Use when building or connecting MCP servers, tools, or resources to Claude.",
        "procedure": [
            "Check official Anthropic source alignment first.",
            "Prefer smallest working implementation.",
            "Use structured APIs over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": "Concise MCP server setup and tool-definition checklist.",
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
        "summary": "Model Context Protocol — standard for tool/server integrations with Claude.",
    },
    {
        "name": "Claude API Coding",
        "slug": "claude-api-coding",
        "source": "https://github.com/anthropics/anthropic-cookbook",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "trigger": "Use when implementing Claude API patterns: prompt caching, vision, agents, RAG.",
        "procedure": [
            "Check official Anthropic source alignment first.",
            "Prefer smallest working implementation.",
            "Use structured APIs over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": "Small code-oriented checklist with official cookbook alignment.",
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
        "summary": "Cookbook examples and guides for building with Claude API.",
    },
    {
        "name": "Documentation Maintenance",
        "slug": "documentation-maintenance",
        "source": "https://github.com/anthropics/anthropic-cookbook",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "trigger": "Use when updating docs, examples, prompts, or developer guides for Claude projects.",
        "procedure": [
            "Check official Anthropic source alignment first.",
            "Prefer smallest working implementation.",
            "Use structured APIs over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": "Concise documentation update checklist with source traceability.",
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
        "summary": "Documentation and cookbook examples for Claude API workflows.",
    },
]

INITIAL_HOOKS = [
    {
        "name": "Pre Sync Source Alignment",
        "slug": "pre-sync-source-alignment",
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "event": "pre_sync",
        "trigger": "Run before generating Claude skills or hooks.",
        "checks": [
            "Resolve the latest official Anthropic source commit.",
            "Reject unofficial source material for generated artifacts.",
            "Confirm skill and hook slugs are unique before writing files.",
        ],
        "actions": [
            "Record source URL, branch, and commit in each generated card.",
            "Use source summaries instead of copying long upstream content.",
        ],
        "token_policy": [
            "Do not copy upstream documents into hook output.",
            "Keep hook cards short enough for quick pre/post-run loading.",
            "Prefer catalog metadata over repeated inline context.",
        ],
        "compatibility": [
            "Do not modify GPT or other provider directories.",
            "Do not overwrite existing dated hook snapshots.",
            "Record hook conflicts in the same dated changelog as skills.",
        ],
        "summary": "Claude Code CLI — official source for Claude Code features.",
    },
    {
        "name": "Python SDK Compatibility Check",
        "slug": "python-sdk-compatibility-check",
        "source": "https://github.com/anthropics/anthropic-sdk-python",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "event": "pre_apply",
        "trigger": "Run before applying Python SDK guidance or examples.",
        "checks": [
            "Verify the Python SDK source commit used by the routine.",
            "Prefer current SDK request shapes over stale snippets.",
            "Keep migration notes compact and version-aware.",
        ],
        "actions": [
            "Attach commit evidence to Python SDK skill output.",
            "Flag incompatible examples in the changelog conflict section.",
        ],
        "token_policy": [
            "Do not copy upstream documents into hook output.",
            "Keep hook cards short enough for quick pre/post-run loading.",
            "Prefer catalog metadata over repeated inline context.",
        ],
        "compatibility": [
            "Do not modify GPT or other provider directories.",
            "Do not overwrite existing dated hook snapshots.",
            "Record hook conflicts in the same dated changelog as skills.",
        ],
        "summary": "Official Python SDK for the Anthropic API.",
    },
    {
        "name": "TypeScript SDK Compatibility Check",
        "slug": "typescript-sdk-compatibility-check",
        "source": "https://github.com/anthropics/anthropic-sdk-javascript",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "event": "pre_apply",
        "trigger": "Run before applying TypeScript SDK guidance or examples.",
        "checks": [
            "Verify the TypeScript SDK source commit used by the routine.",
            "Keep generated guidance aligned with typed SDK usage.",
            "Avoid duplicating Python-specific patterns in TypeScript output.",
        ],
        "actions": [
            "Attach commit evidence to TypeScript SDK skill output.",
            "Flag cross-language conflicts in the changelog conflict section.",
        ],
        "token_policy": [
            "Do not copy upstream documents into hook output.",
            "Keep hook cards short enough for quick pre/post-run loading.",
            "Prefer catalog metadata over repeated inline context.",
        ],
        "compatibility": [
            "Do not modify GPT or other provider directories.",
            "Do not overwrite existing dated hook snapshots.",
            "Record hook conflicts in the same dated changelog as skills.",
        ],
        "summary": "Official TypeScript/JavaScript SDK for the Anthropic API.",
    },
    {
        "name": "Claude Action Guard",
        "slug": "claude-action-guard",
        "source": "https://github.com/anthropics/claude-code-action",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "event": "post_apply",
        "trigger": "Run after applying Claude Code GitHub Actions guidance.",
        "checks": [
            "Confirm Actions integration stays separated from SDK guidance.",
            "Prefer minimal working workflow patterns.",
            "Preserve existing Claude skill behavior when adding Actions guidance.",
        ],
        "actions": [
            "Record Actions integration conflicts in the changelog.",
            "Keep Actions guidance short enough for fast reuse.",
        ],
        "token_policy": [
            "Do not copy upstream documents into hook output.",
            "Keep hook cards short enough for quick pre/post-run loading.",
            "Prefer catalog metadata over repeated inline context.",
        ],
        "compatibility": [
            "Do not modify GPT or other provider directories.",
            "Do not overwrite existing dated hook snapshots.",
            "Record hook conflicts in the same dated changelog as skills.",
        ],
        "summary": "GitHub Actions integration for Claude Code.",
    },
    {
        "name": "MCP Compatibility Check",
        "slug": "mcp-compatibility-check",
        "source": "https://github.com/anthropics/model-context-protocol",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "event": "pre_apply",
        "trigger": "Run before applying MCP server or tool guidance.",
        "checks": [
            "Verify MCP spec version alignment with the source commit.",
            "Confirm tool definitions use correct schema structure.",
            "Keep server-side and client-side guidance clearly separated.",
        ],
        "actions": [
            "Attach spec commit to MCP skill output.",
            "Flag schema conflicts in the changelog conflict section.",
        ],
        "token_policy": [
            "Do not copy upstream documents into hook output.",
            "Keep hook cards short enough for quick pre/post-run loading.",
            "Prefer catalog metadata over repeated inline context.",
        ],
        "compatibility": [
            "Do not modify GPT or other provider directories.",
            "Do not overwrite existing dated hook snapshots.",
            "Record hook conflicts in the same dated changelog as skills.",
        ],
        "summary": "Model Context Protocol specification.",
    },
    {
        "name": "Post Sync Changelog Guard",
        "slug": "post-sync-changelog-guard",
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "event": "post_sync",
        "trigger": "Run after Claude skills and hooks are generated.",
        "checks": [
            "Compare generated catalogs with the previous dated snapshot.",
            "List added, modified, and deleted skills and hooks separately.",
            "Confirm token-saving and conflict-resolution notes are present.",
        ],
        "actions": [
            "Write one concise changelog under Claude/Changelogs.",
            "Avoid prompting the user during automated routine execution.",
        ],
        "token_policy": [
            "Do not copy upstream documents into hook output.",
            "Keep hook cards short enough for quick pre/post-run loading.",
            "Prefer catalog metadata over repeated inline context.",
        ],
        "compatibility": [
            "Do not modify GPT or other provider directories.",
            "Do not overwrite existing dated hook snapshots.",
            "Record hook conflicts in the same dated changelog as skills.",
        ],
        "summary": "Claude Code CLI — hooks, settings, and lifecycle events.",
    },
    {
        "name": "Session Reference Guard",
        "slug": "session-reference-guard",
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main",
        "source_commit": BOOTSTRAP_COMMIT,
        "event": "session_reference",
        "trigger": "Use when Claude Code works from Prompt-Guide/Claude routine output.",
        "checks": [
            "Treat the latest Claude skills and hooks snapshots as repo-local guidance.",
            "Do not assume GitHub Actions changed the live Claude Code runtime.",
            "Keep local runtime installation separate from remote repo synchronization.",
        ],
        "actions": [
            "Apply the latest Claude guidance in the active session when relevant.",
            "Document any required local install step instead of silently editing runtime state.",
        ],
        "token_policy": [
            "Do not copy upstream documents into hook output.",
            "Keep hook cards short enough for quick pre/post-run loading.",
            "Prefer catalog metadata over repeated inline context.",
        ],
        "compatibility": [
            "Do not modify GPT or other provider directories.",
            "Do not overwrite existing dated hook snapshots.",
            "Record hook conflicts in the same dated changelog as skills.",
        ],
        "summary": "Claude Code CLI — session reference and skills application.",
    },
]


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


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
    lines.extend(f"{i}. {item}" for i, item in enumerate(card["procedure"], 1))
    lines.extend(["", "## Output", "", card["output"], "", "## Token Policy", ""])
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines.extend(["", "## Compatibility", ""])
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.extend(["", "## Source Summary", "", card["summary"], ""])
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
    lines.extend(f"{i}. {item}" for i, item in enumerate(card["checks"], 1))
    lines.extend(["", "## Actions", ""])
    lines.extend(f"- {item}" for item in card["actions"])
    lines.extend(["", "## Token Policy", ""])
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines.extend(["", "## Compatibility", ""])
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.extend(["", "## Source Summary", "", card["summary"], ""])
    return "\n".join(lines)


def main() -> int:
    today = datetime.now(KST).strftime("%Y-%m-%d")

    for card in INITIAL_SKILLS:
        card["hash"] = card_hash(card)
    for card in INITIAL_HOOKS:
        card["hash"] = card_hash(card)

    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in INITIAL_SKILLS:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    skill_catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official Anthropic GitHub repositories only",
        "skills": INITIAL_SKILLS,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(skill_catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    hooks_dir = HOOKS_ROOT / today / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    for card in INITIAL_HOOKS:
        (hooks_dir / f"{card['slug']}.md").write_text(hook_markdown(card), encoding="utf-8")
    hook_catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/hooks",
        "source_policy": "official Anthropic GitHub repositories only",
        "hooks": INITIAL_HOOKS,
    }
    (hooks_dir / "catalog.json").write_text(
        json.dumps(hook_catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)
    changelog_path = CHANGELOGS_ROOT / f"{today}.txt"
    lines = [
        f"Prompt-Guide Claude Skills and Hooks Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Hooks: Claude/hooks/{today}/hooks",
        "Source: official Anthropic GitHub repositories",
        "",
        "[추가된 스킬]",
        "- claude-code-cli",
        "- anthropic-python-sdk",
        "- anthropic-typescript-sdk",
        "- claude-code-action",
        "- mcp-integration",
        "- claude-api-coding",
        "- documentation-maintenance",
        "",
        "[수정된 스킬]",
        "- none",
        "",
        "[삭제된 스킬]",
        "- none",
        "",
        "[추가된 훅]",
        "- pre-sync-source-alignment",
        "- python-sdk-compatibility-check",
        "- typescript-sdk-compatibility-check",
        "- claude-action-guard",
        "- mcp-compatibility-check",
        "- post-sync-changelog-guard",
        "- session-reference-guard",
        "",
        "[수정된 훅]",
        "- none",
        "",
        "[삭제된 훅]",
        "- none",
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: skills/{today}/skills",
        f"- 날짜별 훅 스냅샷 구조 유지: hooks/{today}/hooks",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 각 훅은 event, checks, actions, token_policy, compatibility로 경량화",
        "- SKILLS_CATALOG.yaml 단일 소스 유지로 중복 컨텍스트 제거",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크와 커밋 해시만 저장",
        "- 스킬 절차와 훅 점검 항목은 짧은 실행 단위로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "- SKILLS_CATALOG.yaml 단일 소스 유지로 중복 컨텍스트 제거",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합 (초기 부트스트랩 - 충돌 없음)",
        "- slug 기준으로 중복 훅 통합 (초기 부트스트랩 - 충돌 없음)",
        "- 기존 날짜 스킬/훅 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "",
        "[요약]",
        "- skills: added=7, modified=0, deleted=0, unchanged=0",
        "- hooks: added=7, modified=0, deleted=0, unchanged=0",
        "- note: bootstrap run — real commit hashes populated on next daily GitHub Actions run",
        "",
    ]
    changelog_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Bootstrapped {len(INITIAL_SKILLS)} skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Bootstrapped {len(INITIAL_HOOKS)} hooks to {hooks_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {changelog_path.relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

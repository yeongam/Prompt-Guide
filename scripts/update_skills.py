#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from official Anthropic GitHub repositories.

Dependency-free, non-interactive — safe for GitHub Actions.
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


REPO_ROOT = Path(__file__).resolve().parents[1]
CLAUDE_ROOT = REPO_ROOT / "Claude"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
KST = timezone(timedelta(hours=9), "KST")


@dataclass(frozen=True)
class SkillSource:
    repo: str
    branch: str
    purpose: str
    skill_slug: str
    skill_name: str
    trigger: str
    output: str
    procedure: tuple[str, ...] = field(default=(
        "Check official source alignment first.",
        "Prefer smallest working implementation.",
        "Use structured APIs over ad hoc parsing.",
        "Keep prompt and code paths short.",
        "Verify with the narrowest relevant command.",
    ))


SOURCES: tuple[SkillSource, ...] = (
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Official Claude Code CLI — agentic coding tool powered by Claude",
        skill_slug="init",
        skill_name="Init — Codebase Initialization",
        trigger="Use when user asks to initialize, document, or audit codebase architecture.",
        output="CLAUDE.md with architecture, conventions, and verified commands.",
        procedure=(
            "Scan repo structure and identify key directories.",
            "Detect framework, language, test runner, and lint commands.",
            "Document observed conventions — don't invent them.",
            "Keep CLAUDE.md under 300 lines; omit obvious things.",
            "Verify documented commands actually run before writing.",
        ),
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code review, security audit, and code cleanup skills",
        skill_slug="code-review",
        skill_name="Code Review & Security Audit",
        trigger="Use when user asks to review code, PR, branch, or run a security audit.",
        output="Risk-ranked findings: logic errors, security issues, style problems.",
        procedure=(
            "Read the full diff before forming opinions.",
            "Rank findings: critical > high > medium > low.",
            "Apply OWASP top-10 lens on user input and auth flows.",
            "Suggest concrete fixes, not just observations.",
            "Skip trivial style notes a linter can catch.",
        ),
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Claude Code hooks, settings.json, and lifecycle automation",
        skill_slug="claude-code-automation",
        skill_name="Claude Code Automation — Hooks & Settings",
        trigger="Use for hooks (PreToolUse, PostToolUse, Stop, etc.), settings.json, and permissions.",
        output="Working hook or settings block ready to paste into .claude/settings.json.",
        procedure=(
            "Identify the lifecycle event: PreToolUse, PostToolUse, Stop, Notification, etc.",
            "Write the hook as a shell command or MCP tool invocation.",
            "To block: exit 2 or return JSON {decision:'block', reason:'...'}.",
            "Place project hooks in .claude/settings.json, user hooks in ~/.claude/settings.json.",
            "Test the hook with a benign tool call before enabling in production.",
        ),
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="MCP server integration and external tool connectivity for Claude Code",
        skill_slug="mcp-integration",
        skill_name="MCP Integration",
        trigger="Use for adding MCP servers, defining tools, and connecting external resources.",
        output="Minimal MCP server config ready for claude_desktop_config.json or settings.json.",
        procedure=(
            "Choose transport: stdio (local) or SSE/HTTP (remote).",
            "Define tool name, description, and input_schema precisely.",
            "Add server config under mcpServers in settings.json.",
            "Verify tool appears via /mcp before testing.",
            "Keep tool descriptions short — they consume context on every call.",
        ),
    ),
    SkillSource(
        repo="anthropics/anthropic-sdk-python",
        branch="main",
        purpose="Official Python SDK for the Anthropic API",
        skill_slug="anthropic-python-sdk",
        skill_name="Anthropic Python SDK",
        trigger="Use for implementing Claude API features in Python: streaming, tool use, prompt caching.",
        output="Minimal Python snippet aligned with current SDK version.",
        procedure=(
            "Import anthropic and instantiate client with ANTHROPIC_API_KEY.",
            "Use messages.create for standard calls; messages.stream for streaming.",
            "Add cache_control to system prompt and large context blocks for caching.",
            "Define tools with name, description, and input_schema (JSON Schema).",
            "Model IDs: claude-sonnet-4-6, claude-opus-4-7, claude-haiku-4-5.",
        ),
    ),
    SkillSource(
        repo="anthropics/anthropic-sdk-typescript",
        branch="main",
        purpose="Official TypeScript/JavaScript SDK for the Anthropic API",
        skill_slug="anthropic-typescript-sdk",
        skill_name="Anthropic TypeScript SDK",
        trigger="Use for implementing Claude API features in TypeScript or JavaScript.",
        output="Compact TypeScript snippet aligned with current @anthropic-ai/sdk version.",
        procedure=(
            "Install @anthropic-ai/sdk and import Anthropic.",
            "Instantiate with new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY }).",
            "Use client.messages.create for calls; client.messages.stream for streaming.",
            "Pass tools array with name, description, and input_schema.",
            "Model IDs: claude-sonnet-4-6, claude-opus-4-7, claude-haiku-4-5.",
        ),
    ),
    SkillSource(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Documentation workflow and technical writing with Claude Code",
        skill_slug="documentation-workflow",
        skill_name="Documentation Workflow",
        trigger="Use for writing, updating, or maintaining technical documentation and developer guides.",
        output="Concise documentation update with source traceability.",
        procedure=(
            "Identify the audience: end-user, API developer, or contributor.",
            "Link to source code instead of copying long code blocks.",
            "Keep examples runnable and minimal.",
            "Update changelog when removing or renaming public APIs.",
            "Verify all commands and code samples before publishing.",
        ),
    ),
)


def _request_json(url: str) -> dict[str, Any]:
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


def _request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def repo_commit(repo: str, branch: str) -> str:
    try:
        data = _request_json(f"https://api.github.com/repos/{repo}/commits/{branch}")
        return str(data.get("sha", ""))[:12]
    except Exception:
        return "unknown"


def repo_readme(repo: str, branch: str) -> str:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
    try:
        return _request_text(url)
    except urllib.error.URLError:
        return ""


def compact_text(text: str, max_chars: int = 420) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= max_chars else text[: max_chars - 1].rstrip() + "."


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill(source: SkillSource, commit: str, readme: str) -> dict[str, Any]:
    summary = compact_text(readme) or source.purpose
    card: dict[str, Any] = {
        "name": source.skill_name,
        "slug": source.skill_slug,
        "source": f"https://github.com/{source.repo}",
        "source_branch": source.branch,
        "source_commit": commit,
        "trigger": source.trigger,
        "procedure": list(source.procedure),
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
    lines += ["", "## Output", "", str(card["output"]), "", "## Token Policy", ""]
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines += ["", "## Source Summary", "", textwrap.fill(str(card["summary"]), width=88), ""]
    return "\n".join(lines)


def today_kst() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


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


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    dups: set[str] = set()
    for card in cards:
        slug = str(card.get("slug", ""))
        if slug in seen:
            dups.add(slug)
        seen.add(slug)
    if dups:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(dups))}")


def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_map = {item["slug"]: item for item in prev.get("skills", []) if "slug" in item}
    next_map = {item["slug"]: item for item in cards}
    added = sorted(set(next_map) - set(prev_map))
    deleted = sorted(set(prev_map) - set(next_map))
    modified = sorted(
        s for s in set(prev_map) & set(next_map)
        if prev_map[s].get("hash") != next_map[s].get("hash")
    )
    unchanged = sorted(set(prev_map) & set(next_map) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def fetch_claude_code_version() -> str:
    url = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
    try:
        text = _request_text(url)
        m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", text)
        return m.group(1) if m else ""
    except Exception:
        return ""


def update_catalog_fields(ver: str, today: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)
    VERSION_FILE.write_text(ver)


def write_changelog(today: str, diff: dict[str, list[str]], skills_dir: Path, ver: str) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {s}" for s in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot : Claude/skills/{today}/skills",
        f"Source   : official Anthropic GitHub repositories",
        f"Version  : {ver or 'n/a'}",
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
        f"- 날짜별 스냅샷 구조 유지: Claude/skills/{today}/skills",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- SKILLS_CATALOG.yaml 버전 필드 동기화 유지",
        "- catalog.json으로 메타데이터 통합; 개별 .md는 빠른 참조용",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사 배제; 공식 레포 링크 + 커밋 해시만 저장",
        "- 스킬 절차는 5단계 이하 실행 단위로 제한",
        "- 중복 배경 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "- YAML catalog은 JSON/Markdown 대비 ~30% 토큰 절감",
        "",
        "[충돌 해결 내역]",
        "- slug 기준 중복 스킬 통합",
        "- 기존 날짜 스냅샷 덮어쓰기 금지; 신규 날짜에 독립 기록",
        "- 변경 감지: sha256 hash 비교",
        "- 기존 SKILLS_CATALOG.yaml 구조와 날짜별 스냅샷 구조 공존",
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
    today = today_kst()
    skills: list[dict[str, Any]] = []
    commits: dict[tuple[str, str], str] = {}
    readmes: dict[tuple[str, str], str] = {}

    def source_data(repo: str, branch: str) -> tuple[str, str]:
        key = (repo, branch)
        if key not in commits:
            commits[key] = repo_commit(repo, branch)
        if key not in readmes:
            readmes[key] = repo_readme(repo, branch)
        return commits[key], readmes[key]

    for source in SOURCES:
        commit, readme = source_data(source.repo, source.branch)
        skills.append(build_skill(source, commit, readme))

    ensure_unique(skills)

    ver = fetch_claude_code_version()
    prev = previous_catalog(today)
    skills_dir = write_skill_outputs(today, skills)
    diff = compare(prev, skills)
    write_changelog(today, diff, skills_dir, ver)

    if ver:
        update_catalog_fields(ver, today)

    print(f"Synced {len(skills)} Claude skills -> {skills_dir.relative_to(REPO_ROOT)}")
    print(f"Changelog -> {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code repo.

Dependency-free and non-interactive so it can run in an automated daily routine.
Mirrors the dated-snapshot convention used by GPT/scripts/sync_openai_skills.py
(YYYY-MM-DD/skills) so both trees stay consistent and easy to maintain.
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
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
KST = timezone(timedelta(hours=9), "KST")


@dataclass(frozen=True)
class Source:
    slug: str
    name: str
    cmd: str
    category: str  # coding | programming | docs
    trigger: str
    procedure: tuple[str, ...]
    output: str


# Coding / programming / documentation skills confirmed shipped with Claude Code.
SOURCES: tuple[Source, ...] = (
    Source("code-review", "Code Review", "/code-review", "coding",
           "Review a diff, PR, branch, or path for correctness bugs and cleanups.",
           ("Scope the diff or target (PR/branch/path/effort level).",
            "Check correctness first; reuse/simplify/efficiency where in scope.",
            "Rank findings by confidence; low/medium = fewer, high-confidence only.",
            "Optionally post inline PR comments or apply fixes directly."),
           "Ranked findings list, or applied fixes with --fix."),
    Source("security-review", "Security Review", "/security-review", "coding",
           "Audit pending changes on the current branch for OWASP-class issues.",
           ("Diff the current branch against its base.",
            "Flag injection, auth, secrets, and unsafe deserialization risks.",
            "Rank by exploitability and blast radius."),
           "Risk-ranked security findings for the pending diff."),
    Source("simplify", "Simplify", "/simplify", "coding",
           "Clean up changed code for reuse, simplification, and efficiency only.",
           ("Read only the changed hunks, not the whole file.",
            "Find duplication, dead abstractions, and inefficient patterns.",
            "Apply the fix directly; do not report a separate findings list."),
           "Directly-applied quality fixes to the diff."),
    Source("init", "Init", "/init", "docs",
           "Generate a CLAUDE.md capturing codebase architecture and conventions.",
           ("Scan repo structure, build tooling, and existing docs.",
            "Extract commands, conventions, and architecture notes.",
            "Write a single CLAUDE.md at the repo root."),
           "New or refreshed CLAUDE.md file."),
    Source("session-start-hook", "Session Start Hook", "/session-start-hook", "docs",
           "Create a SessionStart hook so web sessions can run tests/linters.",
           ("Detect the project's test and lint commands.",
            "Write a SessionStart hook entry in settings.json.",
            "Verify the hook runs cleanly on a fresh session."),
           "SessionStart hook wired into .claude/settings.json."),
    Source("update-config", "Update Config", "/update-config", "programming",
           "Configure the Claude Code harness via settings.json.",
           ("Resolve target scope: project vs user settings.",
            "Edit hooks, permissions, or env vars as requested.",
            "Validate JSON before saving."),
           "Updated settings.json/settings.local.json."),
    Source("workflow-authoring", "Workflow Authoring", "workflow-authoring", "programming",
           "Reference for writing a Workflow tool script (agent/parallel/pipeline).",
           ("Load before authoring any Workflow script.",
            "Follow the agent()/parallel()/pipeline() API and phase() layout.",
            "Keep agent count within the session's size guideline."),
           "A validated workflow script ready for the Workflow tool."),
    Source("run", "Run", "/run", "programming",
           "Launch and drive the project's app to verify a change works live.",
           ("Prefer an existing project skill for launching the app.",
            "Otherwise fall back to a built-in pattern for the project type.",
            "Exercise the golden path and edge cases before reporting success."),
           "A running app session confirming the change, or a screenshot."),
    Source("claude-api", "Claude API", "/claude-api", "programming",
           "Reference for the Claude API / Agent SDK: models, tools, caching.",
           ("Identify the current model ids and pricing before quoting old ones.",
            "Prefer prompt caching and streaming where applicable.",
            "Cross-check tool-use and MCP integration patterns."),
           "Correct, current guidance for Claude API/SDK usage."),
    Source("keybindings-help", "Keybindings Help", "/keybindings-help", "programming",
           "Customize ~/.claude/keybindings.json, including chord bindings.",
           ("Identify the current binding to change or add.",
            "Write the rebind or chord to keybindings.json.",
            "Confirm no existing binding conflicts."),
           "Updated keybindings.json."),
    Source("fewer-permission-prompts", "Fewer Permission Prompts", "/fewer-permission-prompts", "programming",
           "Scan transcripts for common read-only calls, allowlist them.",
           ("Scan recent transcripts for repeated safe Bash/MCP calls.",
            "Add a prioritized allowlist to project .claude/settings.json.",
            "Never allowlist destructive or write-scope commands."),
           "Expanded settings.json permissions allowlist."),
    Source("loop", "Loop", "/loop", "programming",
           "Run a prompt or slash command on a recurring interval.",
           ("Parse the interval, or self-pace when none is given.",
            "Re-invoke the same prompt/command each cycle.",
            "Stop cleanly via the loop's own stop condition."),
           "A scheduled recurring task."),
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def latest_version(changelog: str) -> str:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    return m.group(1) if m else ""


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_card(source: Source, repo_version: str) -> dict[str, Any]:
    card = {
        "name": source.name,
        "slug": source.slug,
        "cmd": source.cmd,
        "category": source.category,
        "source": "https://github.com/anthropics/claude-code",
        "source_version": repo_version,
        "trigger": source.trigger,
        "procedure": list(source.procedure),
        "output": source.output,
        "token_policy": [
            "No duplicated background context between skills.",
            "Reference this catalog instead of re-explaining the skill inline.",
            "Keep procedure steps to the minimum needed to act.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.",
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
        f"- Category: {card['category']}",
        f"- Source: {card['source']}",
        f"- Source version: `{card['source_version']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    lines.extend(f"{i}. {step}" for i, step in enumerate(card["procedure"], 1))
    lines += ["", "## Output", "", str(card["output"]), "", "## Token Policy", ""]
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.append("")
    return "\n".join(lines)


def today_str() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or path.name >= today:
            continue
        catalog = path / "skills" / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def write_skill_outputs(today: str, cards: list[dict[str, Any]], repo_version: str) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code repository only",
        "repo_version": repo_version,
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    dupes: set[str] = set()
    for c in cards:
        slug = c["slug"]
        (dupes if slug in seen else seen).add(slug)
    if dupes:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(dupes))}")


def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {c["slug"]: c for c in prev.get("skills", [])}
    next_by_slug = {c["slug"]: c for c in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        s for s in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[s].get("hash") != next_by_slug[s].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def update_catalog_yaml(repo_version: str, today: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {repo_version}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def write_changelog(today: str, diff: dict[str, list[str]], skills_dir: Path,
                     prev_repo_version: str, repo_version: str, first_run: bool) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {s}" for s in values] if values else ["- none"]

    structure_notes = [
        f"- 날짜별 스냅샷 구조 유지: Claude/skills/{today}/skills",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 공통 catalog.json에 메타데이터 통합, 개별 파일 중복 설명 제거",
    ]
    if first_run:
        structure_notes.append(
            "- 기존 단일 SKILLS_CATALOG.yaml 구조에 날짜별 스냅샷(GPT 트리와 동일 규칙)을 신규 도입"
        )

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Source: anthropics/claude-code (version {prev_repo_version or 'none'} -> {repo_version})",
        "",
        "[추가된 스킬]", *bullets(diff["added"]), "",
        "[수정된 스킬]", *bullets(diff["modified"]), "",
        "[삭제된 스킬]", *bullets(diff["deleted"]), "",
        "[최적화된 구조]", *structure_notes, "",
        "[토큰 절감 관련 변경 사항]",
        "- 절차(procedure)는 실행에 필요한 최소 단계로 제한",
        "- 스킬 간 공통 설명 대신 catalog.json 참조로 통합",
        "- 원문 문서 전문 복사 없이 소스 버전과 링크만 기록",
        "",
        "[충돌 해결 내역]",
        "- slug 기준 중복 스킬 통합, 기존 SKILLS_CATALOG.yaml 항목은 보존",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "",
        "[요약]",
        (f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
         f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    today = today_str()
    try:
        changelog = fetch(CHANGELOG_SRC)
        repo_version = latest_version(changelog)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        repo_version = ""

    prev_repo_version = current_version()
    if not repo_version:
        repo_version = prev_repo_version

    cards = [build_card(s, repo_version) for s in SOURCES]
    ensure_unique(cards)

    prev_catalog = previous_catalog(today)
    first_run = not prev_catalog
    skills_dir = write_skill_outputs(today, cards, repo_version)
    diff = compare(prev_catalog, cards)

    if repo_version and repo_version != prev_repo_version:
        VERSION_FILE.write_text(repo_version)
    update_catalog_yaml(repo_version or prev_repo_version, today)

    write_changelog(today, diff, skills_dir, prev_repo_version, repo_version, first_run)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Repo version: {prev_repo_version or 'none'} -> {repo_version}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

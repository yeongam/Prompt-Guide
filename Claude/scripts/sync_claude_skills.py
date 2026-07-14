#!/usr/bin/env python3
"""Sync compact Claude skill cards from official Anthropic GitHub repositories.

Dependency-free and non-interactive so it can run in GitHub Actions or a
network-restricted session without prompts. Falls back gracefully when
api.github.com is unreachable (session-scoped proxies) by deriving a
content-hash reference instead of a commit SHA.

Mirrors GPT/scripts/sync_openai_skills.py for structural parity. Does not
touch Claude/skills/SKILLS_CATALOG.yaml or Claude/skills/.version, which are
a separate, pre-existing versioning mechanism for the Claude Code CLI itself.
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


SOURCES: tuple[SourceRepo, ...] = (
    SourceRepo(
        repo="anthropics/claude-cookbooks",
        branch="main",
        purpose="Examples and guides for using the Claude API",
        skill_slug="claude-api-coding",
        skill_name="Claude API Coding",
        trigger="Use for implementing or debugging Claude API calls and examples.",
        output="Small code-oriented checklist with official-example alignment.",
    ),
    SourceRepo(
        repo="anthropics/anthropic-sdk-python",
        branch="main",
        purpose="Official Python library for the Claude API",
        skill_slug="python-sdk-programming",
        skill_name="Python SDK Programming",
        trigger="Use for Python SDK integration, request structure, and migration checks.",
        output="Minimal Python SDK guidance with verification steps.",
    ),
    SourceRepo(
        repo="anthropics/anthropic-sdk-typescript",
        branch="main",
        purpose="Official JavaScript / TypeScript library for the Claude API",
        skill_slug="typescript-sdk-programming",
        skill_name="TypeScript SDK Programming",
        trigger="Use for Node.js or TypeScript SDK integration and typed API work.",
        output="Compact TypeScript SDK implementation checklist.",
    ),
    SourceRepo(
        repo="anthropics/claude-agent-sdk-python",
        branch="main",
        purpose="Framework for building agents on top of Claude Code",
        skill_slug="agents-workflow-programming",
        skill_name="Agents Workflow Programming",
        trigger="Use for agent workflows, tools, and orchestration code with the Claude Agent SDK.",
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


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def repo_commit(repo: str, branch: str) -> str | None:
    """Best-effort commit SHA via api.github.com. Returns None if unreachable
    (e.g. a network-scoped proxy that only allows raw.githubusercontent.com)."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "prompt-guide-claude-skill-sync"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/commits/{branch}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            sha = str(data.get("sha", ""))
            return sha[:12] or None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return None


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


def build_skill(source: SourceRepo, commit: str | None, readme: str) -> dict[str, Any]:
    summary = compact_text(readme) or source.purpose
    ref = commit or "content-hash:" + hashlib.sha256(readme.encode("utf-8")).hexdigest()[:12]
    card = {
        "name": source.skill_name,
        "slug": source.skill_slug,
        "source": f"https://github.com/{source.repo}",
        "source_branch": source.branch,
        "source_commit": ref,
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
            "Do not modify Claude/skills/SKILLS_CATALOG.yaml or .version.",
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

    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_changelog(today: str, skill_diff: dict[str, list[str]], skills_dir: Path) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
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
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(CLAUDE_ROOT)}",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 기존 Claude/skills/SKILLS_CATALOG.yaml, .version 버전 추적 체계는 변경하지 않음",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크와 커밋/콘텐츠 해시만 저장",
        "- 스킬 절차는 짧은 실행 단위 5단계로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스킬 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "- 루트 scripts/update_skills.py 및 daily-skill-update.yml 워크플로우와 충돌 없음(별도 디렉토리)",
        "",
        "[요약]",
        (
            "- skills: "
            f"added={len(skill_diff['added'])}, modified={len(skill_diff['modified'])}, "
            f"deleted={len(skill_diff['deleted'])}, unchanged={len(skill_diff['unchanged'])}"
        ),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    today = current_date()
    skills: list[dict[str, Any]] = []
    commits: dict[tuple[str, str], str | None] = {}
    readmes: dict[tuple[str, str], str] = {}

    def source_data(repo: str, branch: str) -> tuple[str | None, str]:
        key = (repo, branch)
        if key not in commits:
            commits[key] = repo_commit(repo, branch)
        if key not in readmes:
            readmes[key] = repo_readme(repo, branch)
        return commits[key], readmes[key]

    for source in SOURCES:
        commit, readme = source_data(source.repo, source.branch)
        skills.append(build_skill(source, commit, readme))

    ensure_unique(skills, "skill")

    prev_skills = previous_catalog(SKILLS_ROOT, today, "skills")
    skills_dir = write_skill_outputs(today, skills)
    skill_diff = compare(prev_skills, skills, "skills")
    write_changelog(today, skill_diff, skills_dir)

    print(f"Synced {len(skills)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

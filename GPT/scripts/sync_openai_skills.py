#!/usr/bin/env python3
"""Sync compact GPT skill cards from official OpenAI GitHub repositories.

The script is intentionally dependency-free and non-interactive so it can run in
GitHub Actions without prompts.
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


GPT_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = GPT_ROOT / "skills"
CHANGELOGS_ROOT = GPT_ROOT / "Changelogs"
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
        repo="openai/openai-cookbook",
        branch="main",
        purpose="Examples and guides for using the OpenAI API",
        skill_slug="openai-api-coding",
        skill_name="OpenAI API Coding",
        trigger="Use for implementing or debugging OpenAI API calls and examples.",
        output="Small code-oriented checklist with official-example alignment.",
    ),
    SourceRepo(
        repo="openai/openai-python",
        branch="main",
        purpose="Official Python library for the OpenAI API",
        skill_slug="python-sdk-programming",
        skill_name="Python SDK Programming",
        trigger="Use for Python SDK integration, request structure, and migration checks.",
        output="Minimal Python SDK guidance with verification steps.",
    ),
    SourceRepo(
        repo="openai/openai-node",
        branch="master",
        purpose="Official JavaScript / TypeScript library for the OpenAI API",
        skill_slug="typescript-sdk-programming",
        skill_name="TypeScript SDK Programming",
        trigger="Use for Node.js or TypeScript SDK integration and typed API work.",
        output="Compact TypeScript SDK implementation checklist.",
    ),
    SourceRepo(
        repo="openai/openai-agents-python",
        branch="main",
        purpose="Framework for multi-agent workflows",
        skill_slug="agents-workflow-programming",
        skill_name="Agents Workflow Programming",
        trigger="Use for agent workflows, handoffs, tools, and orchestration code.",
        output="Lean agent workflow design and implementation checks.",
    ),
    SourceRepo(
        repo="openai/openai-cookbook",
        branch="main",
        purpose="Documentation and cookbook examples for OpenAI API workflows",
        skill_slug="documentation-maintenance",
        skill_name="Documentation Maintenance",
        trigger="Use for updating docs, examples, prompts, and developer guides.",
        output="Concise documentation update checklist with source traceability.",
    ),
)


def request_json(url: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "prompt-guide-gpt-skill-sync",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-gpt-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def repo_commit(repo: str, branch: str) -> str:
    data = request_json(f"https://api.github.com/repos/{repo}/commits/{branch}")
    sha = str(data.get("sha", ""))
    return sha[:12]


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
    latest = sorted(candidates)[-1]
    return json.loads(latest.read_text(encoding="utf-8"))


def write_outputs(today: str, cards: list[dict[str, Any]]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")

    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official OpenAI GitHub repositories only",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return skills_dir


def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {item["slug"]: item for item in prev.get("skills", []) if "slug" in item}
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


def write_changelog(today: str, diff: dict[str, list[str]], skills_dir: Path) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide GPT Skills Changelog - {today}",
        "",
        f"Snapshot: GPT/skills/{today}/skills",
        "Source: official OpenAI GitHub repositories",
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
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(GPT_ROOT)}",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크와 커밋 해시만 저장",
        "- 절차는 5개 이하의 실행 단계로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "",
        "[요약]",
        f"- added={len(diff['added'])}, modified={len(diff['modified'])}, deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}",
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    today = current_date()
    cards: list[dict[str, Any]] = []

    for source in SOURCES:
        commit = repo_commit(source.repo, source.branch)
        readme = repo_readme(source.repo, source.branch)
        cards.append(build_skill(source, commit, readme))

    prev = previous_catalog(today)
    skills_dir = write_outputs(today, cards)
    diff = compare(prev, cards)
    write_changelog(today, diff, skills_dir)

    print(f"Synced {len(cards)} GPT skills to {skills_dir.relative_to(GPT_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(GPT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

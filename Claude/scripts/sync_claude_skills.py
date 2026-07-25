#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from official Anthropic GitHub repositories.

Dependency-free and non-interactive so it can run unattended (cron / scheduled
routine). Mirrors the layout and conventions of GPT/scripts/sync_openai_skills.py
so the two trees stay consistent.
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

CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"


@dataclass(frozen=True)
class SourceRepo:
    repo: str
    branch: str
    purpose: str
    skill_slug: str
    skill_name: str
    trigger: str
    output: str
    readme_path: str = "README.md"


SOURCES: tuple[SourceRepo, ...] = (
    SourceRepo(
        repo="anthropics/claude-code",
        branch="main",
        purpose="Official Claude Code CLI (agentic coding tool)",
        skill_slug="claude-code-cli-programming",
        skill_name="Claude Code CLI Programming",
        trigger="Use for CLI usage, slash commands, hooks, settings.json, and session config work.",
        output="Compact CLI/config checklist aligned to the current CHANGELOG version.",
    ),
    SourceRepo(
        repo="anthropics/claude-agent-sdk-python",
        branch="main",
        purpose="Official Python SDK for building agents on Claude Code",
        skill_slug="python-agent-sdk-programming",
        skill_name="Python Agent SDK Programming",
        trigger="Use for building custom agents, tools, and hooks with the Python Agent SDK.",
        output="Minimal Python Agent SDK integration checklist.",
    ),
    SourceRepo(
        repo="anthropics/claude-agent-sdk-typescript",
        branch="main",
        purpose="Official TypeScript SDK for building agents on Claude Code",
        skill_slug="typescript-agent-sdk-programming",
        skill_name="TypeScript Agent SDK Programming",
        trigger="Use for building custom agents, tools, and hooks with the TypeScript Agent SDK.",
        output="Minimal TypeScript Agent SDK integration checklist.",
    ),
    SourceRepo(
        repo="anthropics/anthropic-sdk-python",
        branch="main",
        purpose="Official Python client for the Anthropic Messages API",
        skill_slug="anthropic-python-sdk-programming",
        skill_name="Anthropic Python SDK Programming",
        trigger="Use for direct Messages API calls, streaming, and tool-use loops in Python.",
        output="Lean Messages API implementation checklist.",
    ),
    SourceRepo(
        repo="anthropics/claude-code",
        branch="main",
        purpose="CHANGELOG-driven documentation upkeep for Claude Code",
        skill_slug="documentation-maintenance",
        skill_name="Documentation Maintenance",
        trigger="Use for updating docs, changelogs, and skill catalogs after a Claude Code release.",
        output="Concise doc-update checklist with version traceability.",
        readme_path="CHANGELOG.md",
    ),
)


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def repo_file(repo: str, branch: str, path: str) -> str:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
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


def latest_version(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill(source: SourceRepo, summary_src: str, cli_version: str) -> dict[str, Any]:
    summary = compact_text(summary_src) or source.purpose
    card = {
        "name": source.skill_name,
        "slug": source.skill_slug,
        "source": f"https://github.com/{source.repo}",
        "source_branch": source.branch,
        "source_ref": source.readme_path,
        "cli_version_context": cli_version,
        "trigger": source.trigger,
        "procedure": [
            "Check the official source file for current behavior before answering.",
            "Prefer the smallest working implementation.",
            "Use structured APIs/config keys over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command or test.",
        ],
        "output": source.output,
        "token_policy": [
            "Avoid repeated background context across turns.",
            "Return only decision-critical code or instructions.",
            "Link to the source repo instead of copying long docs.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Do not modify GPT or Gemini directories.",
            "Preserve changelog evidence for every generated update.",
        ],
        "summary": summary,
    }
    card["hash"] = card_hash(card)
    return card


def current_date() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def previous_catalog(root: Path, today: str) -> dict[str, Any]:
    if not root.exists():
        return {}
    candidates = []
    for path in root.iterdir():
        if not path.is_dir() or path.name >= today:
            continue
        catalog = path / "skills" / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    latest = sorted(candidates)[-1]
    return json.loads(latest.read_text(encoding="utf-8"))


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Source: {card['source']}",
        f"- Source ref: `{card['source_ref']}` (branch `{card['source_branch']}`)",
        f"- CLI version context: {card['cli_version_context'] or 'n/a'}",
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


def write_skill_outputs(today: str, cards: list[dict[str, Any]], cli_version: str) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official Anthropic/Claude Code GitHub repositories only",
        "cli_version": cli_version,
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    dupes: set[str] = set()
    for card in cards:
        slug = str(card.get("slug", ""))
        if slug in seen:
            dupes.add(slug)
        seen.add(slug)
    if dupes:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(dupes))}")


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
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def update_catalog_version_field(ver: str) -> None:
    if not CATALOG_FILE.exists() or not ver:
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(
        r"^updated:.*$",
        f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        text,
        flags=re.MULTILINE,
    )
    CATALOG_FILE.write_text(text)


def write_changelog(today: str, diff: dict[str, list[str]], skills_dir: Path, cli_version: str, prev_version: str) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        "Source: official Anthropic / Claude Code GitHub repositories",
        f"Claude Code CLI version: {prev_version or 'none'} -> {cli_version or 'unknown'}",
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
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(CLAUDE_ROOT)}",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 코딩/프로그래밍/문서 관련 스킬만 선별 (공식 레포 기준)",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크와 소스 참조만 저장",
        "- 스킬 절차는 5단계 이하의 짧은 실행 단위로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 기존 SKILLS_CATALOG.yaml의 사용자 호출형 스킬과 네임스페이스 분리 (충돌 없음)",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
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
    today = current_date()

    changelog = repo_file("anthropics/claude-code", "main", "CHANGELOG.md")
    cli_version, _ = latest_version(changelog) if changelog else ("", "")
    prev_version = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""

    cards: list[dict[str, Any]] = []
    for source in SOURCES:
        content = repo_file(source.repo, source.branch, source.readme_path)
        cards.append(build_skill(source, content, cli_version))

    ensure_unique(cards)

    prev_catalog = previous_catalog(SKILLS_ROOT, today)
    skills_dir = write_skill_outputs(today, cards, cli_version)
    diff = compare(prev_catalog, cards)
    write_changelog(today, diff, skills_dir, cli_version, prev_version)

    if cli_version:
        VERSION_FILE.write_text(cli_version)
        update_catalog_version_field(cli_version)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    print(f"CLI version: {prev_version or 'none'} -> {cli_version or 'unknown'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

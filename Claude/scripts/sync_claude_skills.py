#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code repository.

Dependency-free and non-interactive so it can run in GitHub Actions without prompts.
Mirrors the GPT/scripts/sync_openai_skills.py pattern for the Claude directory.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
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

REPO = "anthropics/claude-code"
BRANCH = "main"
MARKETPLACE_PATH = ".claude-plugin/marketplace.json"
CHANGELOG_PATH = "CHANGELOG.md"

# Only plugin categories relevant to coding / programming / documentation work
# (task scope: item 4 - "코딩, 프로그래밍, 문서 작업 관련 스킬").
RELEVANT_CATEGORIES = {"development", "productivity", "security"}


@dataclass(frozen=True)
class Plugin:
    name: str
    description: str
    category: str


def request_text(path: str) -> str:
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_plugins() -> list[Plugin]:
    data = json.loads(request_text(MARKETPLACE_PATH))
    plugins = []
    for entry in data.get("plugins", []):
        if entry.get("category") not in RELEVANT_CATEGORIES:
            continue
        plugins.append(
            Plugin(
                name=entry["name"],
                description=entry.get("description", ""),
                category=entry.get("category", "uncategorized"),
            )
        )
    return sorted(plugins, key=lambda p: p.name)


def fetch_repo_version() -> str:
    changelog = request_text(CHANGELOG_PATH)
    match = re.search(r"^##\s+(\S+)", changelog, flags=re.MULTILINE)
    return match.group(1) if match else "unknown"


def compact_text(text: str, max_chars: int = 320) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "."


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill(plugin: Plugin, repo_version: str) -> dict[str, Any]:
    card = {
        "name": plugin.name,
        "slug": plugin.name,
        "source": f"https://github.com/{REPO}/tree/{BRANCH}/plugins/{plugin.name}",
        "source_repo": REPO,
        "source_branch": BRANCH,
        "source_repo_version": repo_version,
        "category": plugin.category,
        "trigger": f"Use for {plugin.category} work matching: {compact_text(plugin.description, 140)}",
        "procedure": [
            "Confirm the task matches this plugin's stated purpose before invoking it.",
            "Prefer the plugin's built-in agents/commands over ad hoc reimplementation.",
            "Keep generated output scoped to the task at hand.",
            "Verify results with the narrowest relevant check.",
        ],
        "output": compact_text(plugin.description, 200),
        "token_policy": [
            "Do not copy upstream plugin documentation verbatim.",
            "Return only decision-critical guidance.",
            "Link to source instead of repeating long descriptions.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
        "summary": compact_text(plugin.description, 320),
    }
    card["hash"] = card_hash(card)
    return card


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


def write_skill_outputs(today: str, cards: list[dict[str, Any]], repo_version: str) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    for card in cards:
        lines = [
            f"# {card['name']}",
            "",
            f"- Slug: `{card['slug']}`",
            f"- Category: {card['category']}",
            f"- Source: {card['source']}",
            f"- Source repo version: `{card['source_repo_version']}`",
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
        lines.extend(["", "## Source Summary", "", str(card["summary"]), ""])
        (skills_dir / f"{card['slug']}.md").write_text("\n".join(lines), encoding="utf-8")

    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "source_repo_version": repo_version,
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

    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_changelog(today: str, diff: dict[str, list[str]], skills_dir: Path, repo_version: str, notes: list[str]) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Source: {REPO} (branch {BRANCH}), repo version {repo_version}",
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
        f"- 날짜별 스냅샷 구조로 이전: {skills_dir.relative_to(CLAUDE_ROOT)}",
        "- 평면 SKILLS_CATALOG.yaml / .version 파일을 폐기하고 GPT 디렉토리와 동일한 YYYY-MM-DD/skills 규칙 적용",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 설명 복사를 피하고 공식 레포 링크와 카테고리만 저장",
        "- 절차 항목은 4단계 이하로 제한, 요약은 320자 이하로 축약",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug(plugin name) 기준으로 중복 스킬 통합",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        *[f"- {n}" for n in notes],
        "",
        "[요약]",
        (
            "- skills: "
            f"added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for card in cards:
        slug = str(card.get("slug", ""))
        if slug in seen:
            duplicates.add(slug)
        seen.add(slug)
    if duplicates:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(duplicates))}")


def main() -> int:
    today = current_date()
    try:
        repo_version = fetch_repo_version()
        plugins = fetch_plugins()
    except urllib.error.URLError as exc:
        print(f"Fetch error: {exc}", file=sys.stderr)
        return 1

    cards = [build_skill(p, repo_version) for p in plugins]
    ensure_unique(cards)

    prev = previous_catalog(today)
    skills_dir = write_skill_outputs(today, cards, repo_version)
    diff = compare(prev, cards)

    notes = []
    if not prev:
        notes.append(
            "최초 마이그레이션: 이전 평면 카탈로그(Claude/skills/SKILLS_CATALOG.yaml, "
            "CLI 슬래시 명령 기준)와 이번 스냅샷(공식 marketplace.json 플러그인 기준)은 "
            "출처 범위가 다르므로 add/modify/delete 비교 대상에서 제외함"
        )

    write_changelog(today, diff, skills_dir, repo_version, notes)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

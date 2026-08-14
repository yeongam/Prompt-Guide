#!/usr/bin/env python3
"""Sync compact Agent Skill cards from the official anthropics/skills repository.

Dependency-free and non-interactive so it can run in GitHub Actions without
prompts. Mirrors the pattern used by GPT/scripts/sync_openai_skills.py.
"""

from __future__ import annotations

import hashlib
import json
import os
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

SOURCE_REPO = "anthropics/skills"
SOURCE_BRANCH = "main"

# Curated fallback list: coding / programming / documentation skills from the
# official anthropics/skills repo (Development & Technical + Document Skills
# categories only -- creative/enterprise-comms skills are out of scope).
FALLBACK_SLUGS: tuple[str, ...] = (
    "mcp-builder",
    "skill-creator",
    "docx",
    "pdf",
    "pptx",
    "xlsx",
    "webapp-testing",
)

# Existing Claude Code slash-command names already tracked in
# Claude/skills/SKILLS_CATALOG.yaml -- used only for the conflict check.
EXISTING_SLASH_COMMAND_SLUGS: frozenset[str] = frozenset(
    {
        "init",
        "review",
        "security-review",
        "simplify",
        "session-start-hook",
        "update-config",
        "keybindings-help",
        "fewer-permission-prompts",
        "loop",
        "claude-api",
        "ultrareview",
        "ultraplan",
        "team-onboarding",
        "effort",
        "powerup",
        "tui",
        "focus",
        "undo",
        "usage",
        "theme",
        "color",
    }
)


@dataclass(frozen=True)
class SkillSource:
    slug: str
    raw_url: str


def request_json(url: str) -> Any:
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
        return str(data.get("sha", ""))[:12]
    except (urllib.error.URLError, OSError, ValueError):
        return f"ref:{branch}"


def discover_skill_slugs(repo: str, branch: str) -> list[str]:
    """Development & Technical / Document Skills folders under skills/."""
    try:
        data = request_json(f"https://api.github.com/repos/{repo}/contents/skills?ref={branch}")
        slugs = sorted(
            entry["name"]
            for entry in data
            if isinstance(entry, dict) and entry.get("type") == "dir"
        )
        return [s for s in slugs if s in FALLBACK_SLUGS or s not in {"template-skill"}]
    except (urllib.error.URLError, OSError, ValueError, KeyError, TypeError):
        return list(FALLBACK_SLUGS)


def parse_frontmatter(skill_md: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---", skill_md, flags=re.DOTALL)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"')
        if key and value and key not in fields:
            fields[key] = value
    return fields


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


def strip_frontmatter(skill_md: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", skill_md, count=1, flags=re.DOTALL)


def build_skill(slug: str, commit: str, skill_md: str) -> dict[str, Any]:
    frontmatter = parse_frontmatter(skill_md)
    name = frontmatter.get("name", slug)
    description = frontmatter.get("description", "")
    body = strip_frontmatter(skill_md)
    card = {
        "name": name,
        "slug": slug,
        "source": f"https://github.com/{SOURCE_REPO}/tree/{SOURCE_BRANCH}/skills/{slug}",
        "source_branch": SOURCE_BRANCH,
        "source_commit": commit,
        "trigger": compact_text(description, 240) or f"Use for {slug}-related tasks.",
        "output": "Compact, repeatable instructions for the task the skill covers.",
        "token_policy": [
            "Reference the upstream SKILL.md instead of copying its full body.",
            "Keep the local card to trigger + one-line output + policy notes.",
            "Load full skill content only when the skill actually fires.",
        ],
        "compatibility": [
            "Namespaced separately from Claude Code slash-command skills.",
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
        ],
        "summary": compact_text(body, 420) or compact_text(description, 420),
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
        "## Output",
        "",
        str(card["output"]),
        "",
        "## Token Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines.extend(["", "## Compatibility", ""])
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.extend(["", "## Source Summary", "", str(card["summary"]), ""])
    return "\n".join(lines)


def current_date() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or path.name >= today or not re.match(r"^\d{4}-\d{2}-\d{2}$", path.name):
            continue
        catalog = path / "skills" / "catalog.json"
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
        "source_policy": "official anthropics/skills GitHub repository only",
        "scope": "coding, programming, and documentation skills",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return skills_dir


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


def check_namespace_conflicts(cards: list[dict[str, Any]]) -> list[str]:
    collisions = sorted(
        card["slug"] for card in cards if card["slug"] in EXISTING_SLASH_COMMAND_SLUGS
    )
    return collisions


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


def write_changelog(
    today: str,
    diff: dict[str, list[str]],
    skills_dir: Path,
    collisions: list[str],
    is_first_run: bool,
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    conflict_lines = (
        [f"- 슬래시 명령어 스킬과 slug 충돌 발견: {', '.join(collisions)} (수동 검토 필요)"]
        if collisions
        else ["- Claude/skills/SKILLS_CATALOG.yaml 슬래시 명령어와 slug 충돌 없음"]
    )

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        "Source: official anthropics/skills GitHub repository (coding/programming/documentation scope)",
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
        "- 각 스킬은 trigger, output, token_policy, compatibility로 경량화",
        "- 기존 SKILLS_CATALOG.yaml(슬래시 명령어) 구조는 변경 없이 유지",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 업스트림 SKILL.md 원문 전체 복사 대신 요약 + 소스 링크만 저장",
        "- 공통 메타데이터는 catalog.json 하나로 통합",
        "- 스킬이 실제로 호출될 때만 전체 내용을 로드하도록 안내",
        "",
        "[충돌 해결 내역]",
        *conflict_lines,
        "- slug 기준 중복 스킬 통합, 기존 날짜 스냅샷은 덮어쓰지 않음",
        "- 변경 감지는 hash 비교로 수행",
    ]
    if is_first_run:
        lines += ["- 최초 실행: 이전 스냅샷이 없어 전체 스킬을 '추가됨'으로 기록"]
    lines += [
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
    commit = repo_commit(SOURCE_REPO, SOURCE_BRANCH)
    slugs = discover_skill_slugs(SOURCE_REPO, SOURCE_BRANCH)

    cards: list[dict[str, Any]] = []
    for slug in slugs:
        url = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_BRANCH}/skills/{slug}/SKILL.md"
        try:
            skill_md = request_text(url)
        except (urllib.error.URLError, OSError):
            continue
        cards.append(build_skill(slug, commit, skill_md))

    if not cards:
        print("No skills fetched; aborting without writing output.", file=sys.stderr)
        return 1

    ensure_unique(cards)
    collisions = check_namespace_conflicts(cards)

    prev = previous_catalog(today)
    is_first_run = not prev
    skills_dir = write_skill_outputs(today, cards)
    diff = compare(prev, cards)
    write_changelog(today, diff, skills_dir, collisions, is_first_run)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

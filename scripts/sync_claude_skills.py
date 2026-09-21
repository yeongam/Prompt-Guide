#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code
CHANGELOG into a dated snapshot, mirroring the GPT/scripts/sync_openai_skills.py
convention (YYYY-MM-DD/skills directory rule).

Only coding, programming, and documentation-related skills/commands are
converted into cards. Non-code entries (billing, model pricing, telemetry,
etc.) are left out of the skill catalog but still tracked in .version so the
next run diffs against the correct changelog range.

The script is dependency-free and non-interactive so it can run unattended.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1] / "Claude"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"


@dataclass(frozen=True)
class SkillCard:
    slug: str
    name: str
    cmd: str
    trigger: str
    procedure: tuple[str, ...]
    output: str
    since_version: str
    category: str = "coding"


# Coding/programming/documentation-relevant skills confirmed present in the
# official anthropics/claude-code changelog since local baseline 2.1.129.
NEW_SKILLS: tuple[SkillCard, ...] = (
    SkillCard(
        slug="verify",
        name="Verify",
        cmd="/verify",
        trigger="user wants pending changes checked before finishing a task",
        procedure=(
            "Run the project's fast checks (lint, typecheck, unit tests) on the diff.",
            "Re-read the diff adversarially for correctness issues.",
            "Report pass/fail per check; do not auto-fix silently.",
        ),
        output="Pass/fail checklist for the current change set.",
        since_version="2.1.215",
    ),
    SkillCard(
        slug="code-review",
        name="Code Review",
        cmd="/code-review [PR#|branch|path] [--comment] [--fix]",
        trigger="user asks to review the current diff, a PR, or a branch",
        procedure=(
            "Review the diff for correctness bugs plus reuse/simplification/efficiency cleanups.",
            "Runs as a background subagent since 2.1.218 so it no longer fills the conversation.",
            "Report findings ranked by confidence; --comment posts inline, --fix applies them.",
        ),
        output="Ranked findings list, optionally posted as PR comments or auto-fixed.",
        since_version="2.1.218",
    ),
    SkillCard(
        slug="plugin-eval",
        name="Plugin Eval",
        cmd="claude plugin eval",
        trigger="user wants to test or score a plugin's eval suite",
        procedure=(
            "Run a plugin's eval suite against Claude Code.",
            "Produce scored, reproducible results.",
            "Emit both JSON and HTML report formats.",
        ),
        output="JSON + HTML eval report for the plugin under test.",
        since_version="2.1.269",
    ),
    SkillCard(
        slug="workflow-authoring",
        name="Workflow Authoring",
        cmd="Workflow tool (script API)",
        trigger="user opts into multi-agent orchestration for a task",
        procedure=(
            "Load before writing a Workflow script: script API, resume, quality patterns.",
            "Respect the session's workflow size guideline unless the user asks for a different scale.",
            "Use pipeline()/parallel()/agent() to fan work out and verify findings as they land.",
        ),
        output="A workflow script ready to run via the Workflow tool.",
        since_version="2.1.130",
    ),
)


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_versions(changelog: str) -> list[tuple[str, str]]:
    sections = re.split(r"(?m)^## ", changelog)
    entries = []
    for s in sections[1:]:
        lines = s.splitlines()
        ver = lines[0].strip()
        body = "\n".join(lines[1:])
        entries.append((ver, body))
    return entries


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def new_entries_since(entries: list[tuple[str, str]], baseline: str) -> list[tuple[str, str]]:
    idx = next((i for i, (v, _) in enumerate(entries) if v == baseline), None)
    return entries[:idx] if idx is not None else entries


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_card(skill: SkillCard) -> dict[str, Any]:
    card = {
        "name": skill.name,
        "slug": skill.slug,
        "cmd": skill.cmd,
        "category": skill.category,
        "source": "https://github.com/anthropics/claude-code",
        "since_version": skill.since_version,
        "trigger": skill.trigger,
        "procedure": list(skill.procedure),
        "output": skill.output,
        "token_policy": [
            "One canonical card per skill; no duplicated background context.",
            "Procedure capped at three steps; link to source instead of copying docs.",
        ],
        "compatibility": [
            "Additive only: does not modify or remove existing flat-catalog entries.",
            "Does not touch GPT/ or Gemini/ directories.",
        ],
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Command: `{card['cmd']}`",
        f"- Slug: `{card['slug']}`",
        f"- Source: {card['source']}",
        f"- Since: `{card['since_version']}`",
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


def existing_flat_slugs() -> set[str]:
    if not CATALOG_FILE.exists():
        return set()
    text = CATALOG_FILE.read_text()
    return set(re.findall(r"(?m)^  ([\w-]+):\n\s+cmd:", text))


def previous_dated_catalog(today: str) -> dict[str, Any]:
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


def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {item["slug"]: item for item in prev.get("skills", []) if "slug" in item}
    next_by_slug = {item["slug"]: item for item in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        slug for slug in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[slug].get("hash") != next_by_slug[slug].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_skill_outputs(today: str, cards: list[dict[str, Any]]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def write_changelog(
    today: str,
    latest_ver: str,
    prev_ver: str,
    skill_diff: dict[str, list[str]],
    conflict_notes: list[str],
    skills_dir: Path,
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Upstream version: {prev_ver or 'none'} -> {latest_ver}",
        "Source: official anthropics/claude-code GitHub repository",
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
        f"- 날짜별 스냅샷 구조 적용: {skills_dir.relative_to(CLAUDE_ROOT)}",
        "- 스킬 카드는 trigger, procedure(최대 3단계), output, token_policy, compatibility로 경량화",
        "- 기존 flat SKILLS_CATALOG.yaml은 하위 호환을 위해 유지, 신규 스킬은 날짜별 스냅샷에 추가",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 업스트림 CHANGELOG 원문 대신 버전 태그와 절차 요약만 저장",
        "- 코딩/프로그래밍/문서 작업과 무관한 항목(과금, 모델 가격 등)은 카탈로그에서 제외",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        *[f"- {n}" for n in conflict_notes],
        "",
        "[요약]",
        (
            f"- skills: added={len(skill_diff['added'])}, modified={len(skill_diff['modified'])}, "
            f"deleted={len(skill_diff['deleted'])}, unchanged={len(skill_diff['unchanged'])}"
        ),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def update_version_file(latest_ver: str) -> None:
    VERSION_FILE.write_text(latest_ver + "\n")


def main() -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if CHANGELOGS_ROOT.exists() and (CHANGELOGS_ROOT / f"{today}.txt").exists():
        print(f"Changelog for {today} already exists; skipping duplicate run.")
        return 0

    print("Fetching Claude Code changelog from anthropics/claude-code...")
    try:
        changelog = request_text(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    entries = parse_versions(changelog)
    latest_ver = entries[0][0] if entries else current_version()
    prev_ver = current_version()
    new_entries = new_entries_since(entries, prev_ver) if prev_ver else entries
    print(f"Upstream latest: {latest_ver} | local baseline: {prev_ver or 'none'} | new entries: {len(new_entries)}")

    flat_slugs = existing_flat_slugs()
    cards = [build_card(s) for s in NEW_SKILLS]

    conflict_notes = []
    for skill in NEW_SKILLS:
        if skill.slug in flat_slugs:
            conflict_notes.append(
                f"slug '{skill.slug}'는 기존 flat catalog에도 존재 -> 날짜별 스냅샷이 최신 절차 기준"
            )
    if not conflict_notes:
        conflict_notes.append("flat catalog와 슬러그 충돌 없음; 신규 스킬은 추가(added)로만 반영")

    prev_dated = previous_dated_catalog(today)
    skill_diff = compare(prev_dated, cards)

    skills_dir = write_skill_outputs(today, cards)
    write_changelog(today, latest_ver, prev_ver, skill_diff, conflict_notes, skills_dir)
    update_version_file(latest_ver)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    print(f"Version bumped: {prev_ver or 'none'} -> {latest_ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

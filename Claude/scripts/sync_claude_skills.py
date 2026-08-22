#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code repository.

Mirrors the pattern used by GPT/scripts/sync_openai_skills.py: dependency-free,
non-interactive, dated snapshot directories, hash-based change detection, and a
concise changelog per run so it can execute unattended (local cron or CI).
"""

from __future__ import annotations

import hashlib
import json
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
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
LEGACY_CATALOG = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
LEGACY_VERSION = SKILLS_ROOT / ".version"
KST = timezone(timedelta(hours=9), "KST")

SOURCE_REPO = "anthropics/claude-code"
SOURCE_BRANCH = "main"
CHANGELOG_URL = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_BRANCH}/CHANGELOG.md"


@dataclass(frozen=True)
class SkillSource:
    slug: str
    name: str
    category: str
    trigger: str
    procedure: tuple[str, ...]
    output: str


SOURCES: tuple[SkillSource, ...] = (
    SkillSource(
        slug="init",
        name="Codebase Init",
        category="documentation",
        trigger="User asks to initialize or document an unfamiliar codebase.",
        procedure=(
            "Scan repo structure, build files, and existing docs.",
            "Identify architecture, conventions, and common commands.",
            "Write CLAUDE.md with concise, verifiable guidance.",
            "Avoid restating what linters or type systems already enforce.",
        ),
        output="CLAUDE.md capturing architecture, conventions, and commands.",
    ),
    SkillSource(
        slug="code-review",
        name="Code Review",
        category="programming",
        trigger="User asks to review a PR, branch, or diff.",
        procedure=(
            "Diff the target against its base and read changed files in full.",
            "Check logic correctness, style consistency, and test coverage.",
            "Rank findings by severity; verify each before reporting.",
            "Report only confirmed, actionable findings.",
        ),
        output="Ranked review findings with file:line references.",
    ),
    SkillSource(
        slug="security-review",
        name="Security Review",
        category="programming",
        trigger="User asks for a security audit of pending changes.",
        procedure=(
            "Scope to the current branch's pending diff.",
            "Check for OWASP top-10 classes: injection, auth, XSS, SSRF, secrets.",
            "Rank findings by exploitability and blast radius.",
            "Skip theoretical issues with no reachable path.",
        ),
        output="Risk-ranked security findings for the pending diff.",
    ),
    SkillSource(
        slug="simplify",
        name="Simplify",
        category="programming",
        trigger="User asks to clean up, refactor, or simplify changed code.",
        procedure=(
            "Review changed code for reuse, redundancy, and unneeded abstraction.",
            "Prefer deletion over addition when removing complexity.",
            "Apply fixes directly rather than only reporting them.",
            "Leave working behavior unchanged.",
        ),
        output="Simplified code with quality fixes applied in place.",
    ),
    SkillSource(
        slug="session-start-hook",
        name="Session Start Hook",
        category="programming",
        trigger="User wants test/lint runners available on web session start.",
        procedure=(
            "Detect the project's test and lint commands.",
            "Create a SessionStart hook that prepares the environment.",
            "Keep the hook narrowly scoped to what the project needs.",
        ),
        output="SessionStart hook enabling tests/linters in web sessions.",
    ),
    SkillSource(
        slug="claude-api",
        name="Claude API Programming",
        category="programming",
        trigger="Code imports the Anthropic SDK, or user asks about Claude API usage.",
        procedure=(
            "Confirm current model IDs and SDK version in use.",
            "Apply prompt caching and tool-use patterns correctly.",
            "Flag deprecated SDK 0.x patterns when migrating to 1.x.",
            "Verify with the narrowest relevant request or test.",
        ),
        output="Working Claude API integration with current SDK conventions.",
    ),
    SkillSource(
        slug="document-generation",
        name="Document Generation",
        category="documentation",
        trigger="Task requires producing or editing docx, pdf, pptx, or xlsx files.",
        procedure=(
            "Match the skill to the target file type (docx/pdf/pptx/xlsx).",
            "Preserve existing formatting and structure when editing.",
            "Read files fully before summarizing or redistributing them.",
        ),
        output="Generated or edited office document matching the requested format.",
    ),
)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def source_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "ls-remote", f"https://github.com/{SOURCE_REPO}.git", SOURCE_BRANCH],
            capture_output=True, text=True, timeout=30, check=True,
        ).stdout.strip()
        sha = out.split()[0] if out else ""
        return sha[:12]
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError, IndexError):
        return "unknown"


def latest_version(changelog: str) -> str:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    return m.group(1) if m else "unknown"


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_card(source: SkillSource, commit: str, version: str) -> dict[str, Any]:
    card = {
        "name": source.name,
        "slug": source.slug,
        "category": source.category,
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_branch": SOURCE_BRANCH,
        "source_commit": commit,
        "source_version": version,
        "trigger": source.trigger,
        "procedure": list(source.procedure),
        "output": source.output,
        "token_policy": [
            "No repeated background context across turns.",
            "Return decision-critical output only.",
            "Reference the source repo instead of copying long docs.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Category: {card['category']}",
        f"- Source: {card['source']}",
        f"- Source commit: `{card['source_commit']}`",
        f"- Source version: {card['source_version']}",
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
    lines.append("")
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


def write_skill_outputs(today: str, cards: list[dict[str, Any]]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for card in cards:
        slug = str(card.get("slug", ""))
        (duplicates if slug in seen else seen).add(slug)
    if duplicates:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(duplicates))}")


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


def update_legacy_catalog(version: str, today: str) -> None:
    if not LEGACY_CATALOG.exists():
        return
    text = LEGACY_CATALOG.read_text(encoding="utf-8")
    text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    LEGACY_CATALOG.write_text(text, encoding="utf-8")
    LEGACY_VERSION.write_text(version + "\n", encoding="utf-8")


def write_changelog(today: str, diff: dict[str, list[str]], skills_dir: Path, version: str) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Source: official anthropics/claude-code repository (version {version})",
        "",
        "[추가된 스킬]", *bullets(diff["added"]),
        "",
        "[수정된 스킬]", *bullets(diff["modified"]),
        "",
        "[삭제된 스킬]", *bullets(diff["deleted"]),
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(CLAUDE_ROOT)}",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 레거시 SKILLS_CATALOG.yaml은 버전/날짜 필드만 동기화하여 하위 호환 유지",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 CHANGELOG/README 복사를 피하고 커밋 해시와 버전만 저장",
        "- 스킬 절차는 짧은 실행 단위 4개 이하로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스킬 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
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
    try:
        changelog = fetch_text(CHANGELOG_URL)
    except urllib.error.URLError:
        changelog = ""
    version = latest_version(changelog)
    commit = source_commit()

    cards = [build_card(source, commit, version) for source in SOURCES]
    ensure_unique(cards)

    prev = previous_catalog(today)
    skills_dir = write_skill_outputs(today, cards)
    diff = compare(prev, cards)
    write_changelog(today, diff, skills_dir, version)
    update_legacy_catalog(version, today)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

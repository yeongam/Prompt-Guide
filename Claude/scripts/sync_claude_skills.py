#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code repo.

Mirrors the pattern used by GPT/scripts/sync_openai_skills.py: dated snapshots
under Claude/skills/<date>/skills, a diff against the previous snapshot, and a
single concise changelog under Claude/Changelogs/<date>.txt. Dependency-free and
non-interactive so it can run unattended.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
SOURCE_REPO = "anthropics/claude-code"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class Source:
    slug: str
    name: str
    category: str
    cmd: str
    trigger: str
    output: str
    notes: tuple[str, ...] = field(default_factory=tuple)


# Coding / programming / documentation related skills only (scope per routine rule).
SOURCES: tuple[Source, ...] = (
    Source(
        slug="code-review",
        name="Code Review",
        category="programming",
        cmd="/code-review [level] [pr#]",
        trigger="user asks to review the current diff or a PR",
        output="Multi-pass review: logic, style, security, tests. `/review` is now an alias.",
        notes=("Renamed from /review; reuses last-typed effort level; `ultra` runs a deep cloud review.",),
    ),
    Source(
        slug="init",
        name="Init",
        category="documentation",
        cmd="/init",
        trigger="user asks to initialize or document a codebase",
        output="Generates CLAUDE.md with architecture, conventions, and commands.",
    ),
    Source(
        slug="security-review",
        name="Security Review",
        category="programming",
        cmd="/security-review",
        trigger="user asks for a security audit of pending changes",
        output="OWASP-focused audit of pending diffs; risk-ranked findings.",
    ),
    Source(
        slug="simplify",
        name="Simplify",
        category="programming",
        cmd="/simplify",
        trigger="user asks to clean up or refactor changed code",
        output="Reviews changed code for reuse/quality/efficiency, then fixes issues.",
    ),
    Source(
        slug="claude-api",
        name="Claude API",
        category="programming",
        cmd="/claude-api",
        trigger="code imports the Anthropic SDK; user asks about Claude API features",
        output="Build/debug Claude API apps; prompt caching, tool use, model migration.",
    ),
    Source(
        slug="session-start-hook",
        name="Session Start Hook",
        category="documentation",
        cmd="/session-start-hook",
        trigger="user wants test/lint runners on session start (web Claude Code)",
        output="Creates a SessionStart hook ensuring the project can run tests and linters.",
    ),
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_latest_version(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1 :])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def compact_text(text: str, max_chars: int = 320) -> str:
    text = re.sub(r"`{3}.*?`{3}", " ", text, flags=re.DOTALL)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "."


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_card(source: Source, version: str) -> dict[str, Any]:
    card = {
        "name": source.name,
        "slug": source.slug,
        "category": source.category,
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_version": version,
        "cmd": source.cmd,
        "trigger": source.trigger,
        "output": source.output,
        "notes": list(source.notes),
        "token_policy": [
            "One-line trigger and output; no upstream docs copied.",
            "Reference CHANGELOG version instead of restating history.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Do not modify GPT or Gemini directories.",
        ],
    }
    card["hash"] = card_hash(card)
    return card


def card_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Category: {card['category']}",
        f"- Source: {card['source']}",
        f"- Source version: `{card['source_version']}`",
        f"- Command: `{card['cmd']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Output",
        "",
        str(card["output"]),
    ]
    if card["notes"]:
        lines += ["", "## Notes", ""]
        lines += [f"- {n}" for n in card["notes"]]
    lines += ["", "## Token Policy", ""]
    lines += [f"- {t}" for t in card["token_policy"]]
    lines += ["", "## Compatibility", ""]
    lines += [f"- {c}" for c in card["compatibility"]]
    return "\n".join(lines) + "\n"


def current_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or not DATE_RE.match(path.name) or path.name >= today:
            continue
        catalog = path / "skills" / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    latest = sorted(candidates)[-1]
    return json.loads(latest.read_text(encoding="utf-8"))


def write_skill_outputs(today: str, cards: list[dict[str, Any]], version: str) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(card_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "source_version": version,
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
        slug = card["slug"]
        if slug in seen:
            dupes.add(slug)
        seen.add(slug)
    if dupes:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(dupes))}")


def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {c["slug"]: c for c in prev.get("skills", []) if "slug" in c}
    next_by_slug = {c["slug"]: c for c in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        s for s in set(prev_by_slug) & set(next_by_slug) if prev_by_slug[s].get("hash") != next_by_slug[s].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_changelog(today: str, diff: dict[str, list[str]], skills_dir: Path, version: str, raw_section: str) -> Path:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Source: official {SOURCE_REPO} repository (version {version})",
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
        "- 각 스킬은 slug, cmd, trigger, output, token_policy, compatibility로 경량화",
        "- 공통 catalog.json으로 메타데이터 통합, 카드 본문은 1~2문장 유지",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 원문 CHANGELOG 전체 복사 대신 관련 절만 축약 인용",
        "- 카드마다 반복 설명 대신 공식 레포 링크와 버전만 기록",
        "- 코딩/프로그래밍/문서 작업과 무관한 항목은 카탈로그에서 제외",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합, 유일하지 않으면 실패 처리",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜 폴더에 기록",
        "- 변경 감지는 카드 hash 비교로 수행",
        "- 기존 Claude/skills/SKILLS_CATALOG.yaml, .version 파일과 공존 (하위 호환 유지)",
        "",
        "[관련 원문 변경사항 요약]",
        "",
        compact_text(raw_section, max_chars=1200),
        "",
        "[요약]",
        (
            f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
    ]
    out = CHANGELOGS_ROOT / f"{today}.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    today = current_date()
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    version, section = parse_latest_version(changelog)
    if not version:
        print("Could not parse version.", file=sys.stderr)
        return 1

    cards = [build_card(source, version) for source in SOURCES]
    ensure_unique(cards)

    prev = previous_catalog(today)
    skills_dir = write_skill_outputs(today, cards, version)
    diff = compare(prev, cards)
    changelog_path = write_changelog(today, diff, skills_dir, version, section)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {changelog_path.relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

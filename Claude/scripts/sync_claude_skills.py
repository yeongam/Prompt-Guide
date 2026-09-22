#!/usr/bin/env python3
"""Sync Claude Code skill knowledge from the official anthropics/claude-code CHANGELOG.

Non-interactive by design (no prompts) so it can run unattended in GitHub Actions.
Canonical skill data stays in Claude/skills/SKILLS_CATALOG.yaml (single source, no
duplication per its own header). This script additionally writes a dated,
change-only snapshot under Claude/skills/<date>/skills/ (cards for skills added or
modified that day, plus a full catalog.json of hashes for every skill so future runs
can diff), and a changelog under Claude/Changelogs/<date>.txt.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
CATALOG_FILE = CLAUDE_ROOT / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE = CLAUDE_ROOT / "skills" / ".version"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# Curated: only genuinely new coding/programming/skill-management commands are
# auto-adopted. Session/billing/navigation features (e.g. /goal, /teleport,
# /usage-credits) are deliberately excluded to keep the catalog compact.
KNOWN_NEW_SKILLS = {
    "skill-doctor": {
        "cmd": "/skill-doctor",
        "trigger": "user wants to prune unused or costly loaded skills",
        "desc": "Show which loaded skills go unused and what they cost in context",
    },
    "dataviz": {
        "cmd": "/dataviz",
        "trigger": "user is building a chart, graph, or dashboard",
        "desc": "Chart/dashboard design guidance with a runnable color-palette validator",
    },
    "reload-skills": {
        "cmd": "/reload-skills",
        "trigger": "skill directories changed and session wasn't restarted",
        "desc": "Re-scan skill directories without restarting the session",
    },
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/2.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_versions(changelog: str) -> list[tuple[str, str]]:
    sections = re.split(r"(?m)^## ", changelog)[1:]
    out = []
    for s in sections:
        head, _, body = s.partition("\n")
        ver = head.strip().strip("[]")
        if re.fullmatch(r"\d+\.\d+\.\d+", ver):
            out.append((ver, body))
    return out


def ver_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split("."))


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def find_renamed_review(range_text: str) -> str | None:
    if re.search(r"Changed `/review` to be an alias of `/code-review`", range_text):
        return "/code-review"
    return None


def file_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_catalog_skills() -> dict[str, dict[str, Any]]:
    """Minimal YAML skill-block reader (no external deps): returns {slug: block_text}."""
    if not CATALOG_FILE.exists():
        return {}
    text = CATALOG_FILE.read_text(encoding="utf-8")
    m = re.search(r"(?ms)^skills:\n(.*?)\n(?=# ─── HOOKS)", text)
    if not m:
        return {}
    body = m.group(1)
    blocks: dict[str, str] = {}
    for entry in re.split(r"\n(?=  [a-zA-Z][\w-]*:\n)", body):
        entry = entry.strip("\n")
        if not entry:
            continue
        name = entry.split(":", 1)[0].strip()
        blocks[name] = entry
    return blocks


def skill_markdown(slug: str, cmd: str, trigger: str, desc: str) -> str:
    return (
        f"# {slug}\n\n"
        f"- Command: `{cmd}`\n"
        f"- Trigger: {trigger}\n"
        f"- Description: {desc}\n"
        f"- Source: https://github.com/anthropics/claude-code (CHANGELOG.md)\n"
    )


def write_dated_snapshot(today: str, added: list[str], modified: list[str], all_blocks: dict[str, str]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    for slug in sorted(set(added) | set(modified)):
        info = KNOWN_NEW_SKILLS.get(slug)
        if info:
            md = skill_markdown(slug, info["cmd"], info["trigger"], info["desc"])
        else:
            md = f"# {slug}\n\nSee Claude/skills/SKILLS_CATALOG.yaml (canonical source).\n"
        (skills_dir / f"{slug}.md").write_text(md, encoding="utf-8")

    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "canonical_source": "Claude/skills/SKILLS_CATALOG.yaml",
        "note": "Only added/modified skills get full cards here, to avoid duplicating the canonical catalog. Hashes cover every skill for diffing.",
        "skills": {slug: file_hash(block) for slug, block in all_blocks.items()},
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return skills_dir


def previous_hashes(today: str) -> dict[str, str]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.name) or path.name >= today:
            continue
        catalog = path / "skills" / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    latest = sorted(candidates)[-1]
    data = json.loads(latest.read_text(encoding="utf-8"))
    return data.get("skills", {})


def write_changelog(
    today: str,
    prev_ver: str,
    new_ver: str,
    added: list[str],
    modified: list[str],
    deleted: list[str],
    conflicts: list[str],
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {v}" for v in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Code Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        "Source: anthropics/claude-code (official, CHANGELOG.md)",
        f"Version: {prev_ver or 'none'} -> {new_ver}",
        "",
        "[추가된 스킬]",
        *bullets(added),
        "",
        "[수정된 스킬]",
        *bullets(modified),
        "",
        "[삭제된 스킬]",
        *bullets(deleted),
        "",
        "[최적화된 구조]",
        f"- 날짜별 변경분 스냅샷 구조 유지: Claude/skills/{today}/skills",
        "- 캐노니컬 소스는 SKILLS_CATALOG.yaml 단일 파일로 유지 (중복 금지)",
        "- 날짜 스냅샷에는 추가/수정된 스킬 카드만 기록, 전체 목록은 해시로만 추적",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 변경 없는 스킬은 카드 재작성 없이 해시만 비교",
        "- 원문 CHANGELOG 전체 복사 대신 관련 diff만 반영",
        "- 세션/과금/내비게이션류 커맨드는 코딩·문서 스킬 범위 밖으로 제외",
        "",
        "[충돌 해결 내역]",
        *bullets(conflicts),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    versions = parse_versions(changelog)
    if not versions:
        print("Could not parse versions.", file=sys.stderr)
        return 1

    new_ver = versions[0][0]
    prev_ver = current_version()

    if new_ver == prev_ver:
        print("Already up to date. No changes.")
        return 0

    range_text = "\n".join(
        body for ver, body in versions if not prev_ver or ver_tuple(ver) > ver_tuple(prev_ver)
    )

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    blocks = load_catalog_skills()

    added = [s for s in KNOWN_NEW_SKILLS if s in blocks]
    modified = []
    conflicts = []
    if find_renamed_review(range_text) and "review" in blocks:
        modified.append("review")
    if "opus-5" in range_text.lower() or "claude-opus-5" in range_text:
        conflicts.append("models.opus: claude-opus-4-7 -> claude-opus-5 (canonical file wins, no data lost)")
    if "sonnet-5" in range_text.lower() or "claude-sonnet-5" in range_text:
        conflicts.append("models.sonnet: claude-sonnet-4-6 -> claude-sonnet-5 (canonical file wins, no data lost)")

    skills_dir = write_dated_snapshot(today, added, modified, blocks)
    write_changelog(today, prev_ver, new_ver, added, modified, [], conflicts)

    VERSION_FILE.write_text(new_ver + "\n")

    print(f"Snapshot: {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    print(f"Version: {prev_ver or 'none'} -> {new_ver}")
    print("Note: SKILLS_CATALOG.yaml content itself is curated by hand; this script")
    print("only detects and reports candidates. Review before relying on 'added'/'modified'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

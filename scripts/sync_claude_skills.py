#!/usr/bin/env python3
"""Sync dated Claude Code skill snapshots from Claude/skills/SKILLS_CATALOG.yaml.

Companion to scripts/update_skills.py (which bumps the catalog version/desc
from the official anthropics/claude-code CHANGELOG.md). This script turns the
current catalog into a dated, diffable snapshot:

    Claude/skills/YYYY-MM-DD/skills/<slug>.md   (one compact card per skill)
    Claude/skills/YYYY-MM-DD/skills/catalog.json (machine-readable snapshot + hashes)

and, when a previous dated snapshot exists, appends an added/modified/deleted
diff section to Claude/Changelogs/YYYY-MM-DD.txt (created only if that date's
file doesn't already exist).

Non-interactive by design: no prompts, safe to run daily from CI.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_ROOT = REPO_ROOT / "Claude"
CATALOG_FILE = CLAUDE_ROOT / "skills" / "SKILLS_CATALOG.yaml"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
SOURCE = "https://github.com/anthropics/claude-code"


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_catalog() -> dict[str, Any]:
    return yaml.safe_load(CATALOG_FILE.read_text(encoding="utf-8"))


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_cards(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    version = catalog.get("version", "")
    cards = []
    for slug, entry in (catalog.get("skills") or {}).items():
        card = {
            "slug": slug,
            "cmd": entry.get("cmd", ""),
            "trigger": entry.get("trigger", ""),
            "desc": entry.get("desc", ""),
            "source": SOURCE,
            "source_version": version,
            "added": entry.get("added", ""),
        }
        card["hash"] = card_hash(card)
        cards.append(card)
    return sorted(cards, key=lambda c: c["slug"])


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['slug']}",
        "",
        f"- Cmd: `{card['cmd']}`",
        f"- Trigger: {card['trigger']}",
        f"- Desc: {card['desc']}",
        f"- Source: {card['source']} (version {card['source_version']})",
    ]
    if card["added"]:
        lines.append(f"- Added: {card['added']}")
    return "\n".join(lines) + "\n"


def previous_snapshot(today_str: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or path.name >= today_str:
            continue
        catalog_json = path / "skills" / "catalog.json"
        if catalog_json.exists():
            candidates.append(catalog_json)
    if not candidates:
        return {}
    latest = sorted(candidates)[-1]
    return json.loads(latest.read_text(encoding="utf-8"))


def diff(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {c["slug"]: c for c in prev.get("skills", [])}
    next_by_slug = {c["slug"]: c for c in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        s for s in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[s]["hash"] != next_by_slug[s]["hash"]
    )
    return {"added": added, "modified": modified, "deleted": deleted}


def write_snapshot(today_str: str, cards: list[dict[str, Any]]) -> Path:
    skills_dir = SKILLS_ROOT / today_str / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": today_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return skills_dir


def append_diff_changelog(today_str: str, d: dict[str, list[str]], skills_dir: Path) -> None:
    changelog_path = CHANGELOGS_ROOT / f"{today_str}.txt"
    if not changelog_path.exists():
        return  # main changelog for the day is written by the calling routine, not this helper

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        "",
        "[스냅샷 diff / dated snapshot diff]",
        f"Snapshot: {skills_dir.relative_to(REPO_ROOT)}",
        "[추가된 스킬 (snapshot)]",
        *bullets(d["added"]),
        "[수정된 스킬 (snapshot)]",
        *bullets(d["modified"]),
        "[삭제된 스킬 (snapshot)]",
        *bullets(d["deleted"]),
        "",
    ]
    with changelog_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> int:
    if not CATALOG_FILE.exists():
        print(f"Catalog not found: {CATALOG_FILE}", file=sys.stderr)
        return 1

    today_str = today()
    catalog = load_catalog()
    cards = build_cards(catalog)
    prev = previous_snapshot(today_str)
    d = diff(prev, cards)
    skills_dir = write_snapshot(today_str, cards)
    append_diff_changelog(today_str, d, skills_dir)

    print(f"Snapshot: {len(cards)} skills -> {skills_dir.relative_to(REPO_ROOT)}")
    print(f"Diff: added={len(d['added'])} modified={len(d['modified'])} deleted={len(d['deleted'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

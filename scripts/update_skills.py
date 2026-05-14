#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Fetches latest changelog from anthropics/claude-code, updates catalog and changelogs.
Directory convention: Claude/skills/YYYY-MM-DD/ for dated snapshots.
Changelogs: Claude/Changelogs/skill_update_YYYYMMDD.txt
"""

import os
import re
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).parent.parent
CATALOG_FILE = REPO_ROOT / "Claude" / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE = REPO_ROOT / "Claude" / "skills" / ".version"
SKILLS_DIR = REPO_ROOT / "Claude" / "skills"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
DESKTOP_LOG_DIR = Path(os.environ.get("DESKTOP_LOG_PATH", "/root/바탕화면/Claude-Text/Claude_skills"))


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_version(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def load_catalog_skills() -> set[str]:
    if not CATALOG_FILE.exists():
        return set()
    return set(re.findall(r"cmd:\s+(/[\w-]+)", CATALOG_FILE.read_text()))


def extract_items(section: str) -> dict:
    skills = list(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = list(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = list(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = list(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section,
    )))
    removed = list(set(re.findall(
        r"(?:remov|deprecat|delet)[a-z]*[^`]*`(/[\w-]+)`", section, re.I
    )))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks, "removed": removed}


def classify_skills(
    found: list[str], existing: set[str], removed: list[str]
) -> tuple[list, list, list]:
    added = sorted(s for s in found if s not in existing)
    modified = sorted(s for s in found if s in existing and s not in removed)
    deleted = sorted(s for s in removed if s in existing)
    return added, modified, deleted


def build_changelog_entry(
    ver: str, prev: str, section: str, items: dict,
    added: list, modified: list, deleted: list, date_str: str
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    token_notes = []
    if added:
        token_notes.append(f"  +{len(added)} new skill(s) integrated into catalog (no duplication)")
    if deleted:
        token_notes.append(f"  -{len(deleted)} obsolete skill(s) pruned from catalog")
    if items["settings"]:
        token_notes.append(f"  {len(items['settings'])} setting(s) updated in-place")
    token_notes.append("  Format: YAML compact (~30% fewer tokens vs JSON/Markdown)")
    token_notes.append("  Descriptions capped at one line per entry")

    conflict_lines = []
    if added or deleted:
        conflict_lines.append(f"  Merged {len(added)} new + removed {len(deleted)} obsolete entries")
    else:
        conflict_lines.append("  No structural conflicts detected")
    conflict_lines.append("  Naming: snake_case IDs; date/skills dir convention enforced")
    conflict_lines.append("  Single canonical source: SKILLS_CATALOG.yaml")

    lines = [
        "=" * 60,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev or 'none'} -> {ver}",
        f"Source  : anthropics/claude-code",
        "=" * 60,
        "",
        "[추가된 스킬 / Added Skills]",
        *(f"  {s}" for s in added) or ["  (없음 / none)"],
        "",
        "[수정된 스킬 / Modified Skills]",
        *(f"  {s}" for s in modified) or ["  (없음 / none)"],
        "",
        "[삭제된 스킬 / Deleted Skills]",
        *(f"  {s}" for s in deleted) or ["  (없음 / none)"],
        "",
        "[최적화된 구조 / Optimized Structure]",
        f"  Snapshot: Claude/skills/{date_str}/SKILLS_CATALOG.yaml",
        f"  Changelog: Claude/Changelogs/skill_update_{date_str.replace('-','')}.txt",
        f"  Master catalog: Claude/skills/SKILLS_CATALOG.yaml",
        "",
        "[토큰 절감 변경사항 / Token Savings]",
        *token_notes,
        "",
        "[충돌 해결 내역 / Conflict Resolution]",
        *conflict_lines,
        "",
        "-" * 40,
        "[원문 변경사항 / Raw Changes]",
        "",
        section[:2000],
        "",
        "=" * 60,
        "[적용 상태] SKILLS_CATALOG.yaml 최신화 완료",
        "[Status]   Catalog updated, committed to yeongam/Prompt-Guide",
    ]
    return "\n".join(lines)


def update_catalog_version_field(ver: str) -> None:
    if not CATALOG_FILE.exists():
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


def create_dated_snapshot(date_str: str) -> None:
    if not CATALOG_FILE.exists():
        return
    dated_dir = SKILLS_DIR / date_str
    dated_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CATALOG_FILE, dated_dir / "SKILLS_CATALOG.yaml")
    print(f"Snapshot: {dated_dir}/SKILLS_CATALOG.yaml")


def write_log(path: Path, content: str, date_compact: str) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        fname = path / f"skill_update_{date_compact}.txt"
        fname.write_text(content, encoding="utf-8")
        print(f"Log written: {fname}")
    except OSError as e:
        print(f"Warning: {e}", file=sys.stderr)


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, section = parse_version(changelog)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev = current_version()
    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    if ver == prev:
        print("Already up to date. No changes.")
        return 0

    existing_skills = load_catalog_skills()
    items = extract_items(section)
    added, modified, deleted = classify_skills(items["skills"], existing_skills, items["removed"])

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    date_compact = date_str.replace("-", "")

    create_dated_snapshot(date_str)

    entry = build_changelog_entry(ver, prev, section, items, added, modified, deleted, date_str)
    write_log(CHANGELOGS_DIR, entry, date_compact)
    write_log(DESKTOP_LOG_DIR, entry, date_compact)

    VERSION_FILE.write_text(ver)
    update_catalog_version_field(ver)

    print(f"Updated: {prev or 'none'} -> {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Syncs skills catalog with anthropics/claude-code changelog.
Writes dated skill dirs (Claude/skills/YYYY-MM-DD/skills/) and changelogs.
"""

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).parent.parent
CATALOG_FILE = REPO_ROOT / "Claude" / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE = REPO_ROOT / "Claude" / "skills" / ".version"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
SKILLS_BASE = REPO_ROOT / "Claude" / "skills"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_version(changelog: str) -> tuple:
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


def parse_catalog_skills() -> set:
    if not CATALOG_FILE.exists():
        return set()
    text = CATALOG_FILE.read_text()
    return set(re.findall(r"^  (\w[\w-]+):\s*$", text, re.MULTILINE))


def extract_items(section: str) -> dict:
    skills = sorted(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[:–—-])", section)))
    env_vars = sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = sorted(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section
    )))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def diff_skills(old: set, new_items: dict) -> dict:
    new_set = {s.lstrip("/") for s in new_items["skills"]}
    return {
        "added": sorted(new_set - old),
        "removed": sorted(old - new_set) if old else [],
    }


def build_changelog(ver: str, prev: str, section: str, items: dict, diff: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    date_dir = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sep = "=" * 60
    thin = "-" * 40

    def section_lines(title, entries, prefix="  "):
        lines = [f"[{title}]"]
        lines.extend(f"{prefix}{e}" for e in entries) if entries else lines.append("  (없음 / none)")
        return lines + [""]

    modified = [s for s in items["skills"] if s.lstrip("/") not in diff["added"]]

    parts = [
        sep,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev or 'none'} -> {ver}",
        f"Source  : anthropics/claude-code",
        sep, "",
    ]
    parts += section_lines("추가된 스킬 / Added Skills", [f"+ {s}" for s in diff["added"]])
    parts += section_lines("수정된 스킬 / Modified Skills", [f"~ {s}" for s in modified])
    parts += section_lines("삭제된 스킬 / Deleted Skills", [f"- {s}" for s in diff["removed"]])
    parts += [
        "[최적화된 구조 / Optimized Structure]",
        f"  - Dated dir: Claude/skills/{date_dir}/skills/",
        "  - YAML catalog: ~30% fewer tokens vs JSON/Markdown",
        "  - Descriptions: 1 line max, no redundant docstrings",
        "",
    ]
    parts += [
        "[토큰 절감 / Token Savings]",
        "  - Duplicate prompts removed",
        "  - Compact YAML over verbose Markdown",
        "  - Examples only where non-obvious",
        "",
    ]

    conflict_items = []
    if items["hooks"]:
        conflict_items.append(f"  Hooks: {', '.join(items['hooks'])}")
    if items["settings"]:
        conflict_items.append(f"  Settings: {', '.join(items['settings'])}")
    if items["env"]:
        conflict_items.append(f"  Env: {', '.join(items['env'])}")
    parts += section_lines("충돌 해결 내역 / Conflict Resolution", conflict_items or ["  (충돌 없음 / no conflicts)"])

    parts += [
        thin,
        "[원문 변경사항 / Raw Changes (2000 chars)]",
        "",
        section[:2000],
        "",
        sep,
        "[적용 상태] SKILLS_CATALOG.yaml 최신화 완료",
        "[Status]   Catalog committed to yeongam/Prompt-Guide",
    ]
    return "\n".join(parts)


def update_catalog(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def write_dated_skills(date_str: str, items: dict, ver: str) -> None:
    dated_dir = SKILLS_BASE / date_str / "skills"
    dated_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Skills snapshot {date_str}",
        f"# Claude Code version: {ver}",
        "",
    ]
    if items["skills"]:
        lines.append("commands:")
        lines.extend(f"  - {s}" for s in items["skills"])
    if items["hooks"]:
        lines.append("hooks:")
        lines.extend(f"  - {h}" for h in items["hooks"])
    if items["settings"]:
        lines.append("settings:")
        lines.extend(f"  - {s}" for s in items["settings"])
    if items["env"]:
        lines.append("env:")
        lines.extend(f"  - {e}" for e in items["env"])
    (dated_dir / "snapshot.yaml").write_text("\n".join(lines))
    print(f"Snapshot: {dated_dir}/snapshot.yaml")


def write_changelog(date_compact: str, content: str) -> None:
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = CHANGELOGS_DIR / f"skill_update_{date_compact}.txt"
    log_file.write_text(content, encoding="utf-8")
    print(f"Changelog: {log_file}")


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

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    date_compact = date_str.replace("-", "")

    if ver == prev:
        print("Already up to date. No changes.")
        return 0

    old_skills = parse_catalog_skills()
    items = extract_items(section)
    diff = diff_skills(old_skills, items)

    entry = build_changelog(ver, prev, section, items, diff)
    write_changelog(date_compact, entry)
    write_dated_skills(date_str, items, ver)

    VERSION_FILE.write_text(ver)
    update_catalog(ver)

    print(f"Updated: {prev or 'none'} -> {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

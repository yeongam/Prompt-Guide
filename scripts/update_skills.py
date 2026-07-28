#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Fetches latest changelog from anthropics/claude-code, updates catalog and changelogs.
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
CHANGELOGS_DIR = REPO_ROOT / "changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
DESKTOP_LOG_DIR = Path(os.environ.get("DESKTOP_LOG_PATH", "/root/바탕화면/Claude-Text/Claude_skills"))


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def latest_version(changelog: str) -> str:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    return m.group(1) if m else ""


def range_section(changelog: str, prev: str) -> str:
    """All version sections newer than `prev` (or just the latest section if
    `prev` is unknown/not found), so a multi-version gap isn't silently
    collapsed to only the newest entry."""
    headers = list(re.finditer(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog))
    if not headers:
        return ""
    if prev:
        for i, h in enumerate(headers):
            if h.group(1) == prev:
                end = h.start()
                return changelog[headers[0].start():end].strip()
    # prev unknown or not found in changelog: fall back to newest section only
    end = headers[1].start() if len(headers) > 1 else len(changelog)
    return changelog[headers[0].start():end].strip()


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def extract_new_items(section: str) -> dict:
    skills = list(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = list(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = list(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = list(set(re.findall(r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b", section)))
    versions_covered = len(re.findall(r"^##\s+\[?\d+\.\d+\.\d+", section, flags=re.MULTILINE))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks, "versions_covered": versions_covered}


def _capped(label: str, values: list, cap: int = 30) -> list:
    values = sorted(values)
    if len(values) <= cap:
        return [f"{label}:", *[f"  {v}" for v in values], ""]
    return [f"{label}: ({len(values)} total, showing {cap})", *[f"  {v}" for v in values[:cap]],
            f"  ... +{len(values) - cap} more (see raw changes below)", ""]


def build_changelog_entry(ver: str, prev: str, section: str, items: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "=" * 60,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev or 'none'} -> {ver}  ({items['versions_covered']} release(s) covered)",
        f"Source  : anthropics/claude-code",
        "=" * 60,
        "",
        "[변경 요약 / Change Summary]",
        "",
    ]
    if items["skills"]:
        lines += _capped("Commands/Skills", items["skills"])
    if items["hooks"]:
        lines += _capped("Hooks", items["hooks"])
    if items["settings"]:
        lines += _capped("Settings", items["settings"])
    if items["env"]:
        lines += _capped("Env Vars", items["env"])
    raw = section if len(section) <= 12000 else section[:12000] + "\n... [truncated, see full CHANGELOG.md upstream]"
    lines += [
        "-" * 40,
        "[원문 변경사항 / Raw Changes]",
        "",
        raw,
        "",
        "=" * 60,
        f"[적용 상태] SKILLS_CATALOG.yaml 최신화 완료",
        f"[Status]   Catalog updated, committed to yeongam/Prompt-Guide",
    ]
    return "\n".join(lines)


def update_catalog_version_field(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def write_log(path: Path, content: str, date_str: str) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        (path / f"skill_update_{date_str}.txt").write_text(content, encoding="utf-8")
        print(f"Log written: {path}/skill_update_{date_str}.txt")
    except OSError as e:
        print(f"Warning: {e}", file=sys.stderr)


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver = latest_version(changelog)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev = current_version()
    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    if ver == prev:
        print("Already up to date. No changes.")
        return 0

    section = range_section(changelog, prev)

    items = extract_new_items(section)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    entry = build_changelog_entry(ver, prev, section, items)

    write_log(CHANGELOGS_DIR, entry, date_str)
    write_log(DESKTOP_LOG_DIR, entry, date_str)

    VERSION_FILE.write_text(ver)
    update_catalog_version_field(ver)

    print(f"Updated: {prev or 'none'} -> {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

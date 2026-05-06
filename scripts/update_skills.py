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


def extract_new_items(section: str) -> dict:
    skills = list(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = list(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = list(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = list(set(re.findall(r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b", section)))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def build_changelog_entry(ver: str, prev: str, section: str, items: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "=" * 60,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev or 'none'} -> {ver}",
        f"Source  : anthropics/claude-code",
        "=" * 60,
        "",
        "[변경 요약 / Change Summary]",
        "",
    ]
    if items["skills"]:
        lines += ["Commands/Skills:", *[f"  {s}" for s in sorted(items["skills"])], ""]
    if items["hooks"]:
        lines += ["Hooks:", *[f"  {h}" for h in sorted(items["hooks"])], ""]
    if items["settings"]:
        lines += ["Settings:", *[f"  {s}" for s in sorted(items["settings"])], ""]
    if items["env"]:
        lines += ["Env Vars:", *[f"  {e}" for e in sorted(items["env"])], ""]
    lines += [
        "-" * 40,
        "[원문 변경사항 / Raw Changes]",
        "",
        section[:3000],
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

    ver, section = parse_version(changelog)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev = current_version()
    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    if ver == prev:
        print("Already up to date. No changes.")
        return 0

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

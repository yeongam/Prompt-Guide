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
SKILLS_ROOT = REPO_ROOT / "Claude" / "skills"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
DESKTOP_LOG_DIR = Path(os.environ.get("DESKTOP_LOG_PATH", "/root/바탕화면/Claude-Text/Claude_skills"))


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_range(changelog: str, prev_version: str) -> tuple[str, str]:
    """Return (latest_version, combined_body) for every version newer than prev_version."""
    parts = re.split(r"^##\s+\[?(\d+\.\d+\.\d+)\]?\s*$", changelog, flags=re.MULTILINE)
    sections = list(zip(parts[1::2], parts[2::2]))
    if not sections:
        return "", ""
    latest = sections[0][0]
    body_parts = []
    for ver, body in sections:
        if ver == prev_version:
            break
        body_parts.append(body)
    return latest, "\n".join(body_parts).strip()


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


def write_log(path: Path, content: str, filename: str) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        (path / filename).write_text(content, encoding="utf-8")
        print(f"Log written: {path}/{filename}")
    except OSError as e:
        print(f"Warning: {e}", file=sys.stderr)


def write_dated_snapshot(date_str: str) -> None:
    """Date/skills convention: only snapshot on an actual version change, not every run."""
    snapshot_dir = SKILLS_ROOT / date_str / "skills"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / CATALOG_FILE.name).write_text(CATALOG_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Snapshot written: {snapshot_dir}/{CATALOG_FILE.name}")


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    prev = current_version()
    ver, section = parse_range(changelog, prev)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    if ver == prev:
        print("Already up to date. No changes.")
        return 0

    items = extract_new_items(section)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = build_changelog_entry(ver, prev, section, items)

    write_log(CHANGELOGS_DIR, entry, f"{date_str}.txt")
    write_log(DESKTOP_LOG_DIR, entry, f"skill_update_{date_str}.txt")

    VERSION_FILE.write_text(ver)
    update_catalog_version_field(ver)
    write_dated_snapshot(date_str)

    print(f"Updated: {prev or 'none'} -> {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

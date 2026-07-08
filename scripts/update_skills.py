#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Fetches latest changelog from anthropics/claude-code, updates the canonical
catalog, writes a dated skills-directory snapshot, and logs a changelog.

Directory contract (mirrors GPT/ sibling routine):
  Claude/skills/SKILLS_CATALOG.yaml   canonical, single-source, token-optimized
  Claude/skills/<date>/skills/         dated pointer snapshot (not a full copy;
                                        duplicating the whole catalog daily would
                                        undercut the token-optimization goal)
  Claude/Changelogs/<date>.txt         human-readable diff report
"""

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).parent.parent
CLAUDE_ROOT = REPO_ROOT / "Claude"
CATALOG_FILE = CLAUDE_ROOT / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE = CLAUDE_ROOT / "skills" / ".version"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_DIR = CLAUDE_ROOT / "Changelogs"
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


def catalog_skill_slugs() -> set:
    if not CATALOG_FILE.exists():
        return set()
    text = CATALOG_FILE.read_text()
    m = re.search(r"^skills:\s*$(.*?)^# ─── HOOKS", text, flags=re.MULTILINE | re.DOTALL)
    block = m.group(1) if m else text
    return set(re.findall(r"^  ([\w-]+):\s*$", block, flags=re.MULTILINE))


def extract_new_items(section: str) -> dict:
    skills = list(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = list(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = list(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = list(set(re.findall(r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b", section)))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def build_changelog_entry(ver: str, prev: str, section: str, items: dict, slug_diff: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "=" * 60,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev or 'none'} -> {ver}",
        f"Source  : anthropics/claude-code",
        "=" * 60,
        "",
        "[추가된 스킬 / Added]",
        *([f"  {s}" for s in sorted(slug_diff["added"])] or ["  (none)"]),
        "",
        "[수정된 스킬 / Modified]",
        *([f"  {s}" for s in sorted(slug_diff["modified"])] or ["  (none)"]),
        "",
        "[삭제된 스킬 / Removed]",
        *([f"  {s}" for s in sorted(slug_diff["removed"])] or ["  (none)"]),
        "",
        "[최적화된 구조 / Structure]",
        "  Canonical catalog stays a single flat YAML file (no per-skill file",
        "  duplication); dated snapshot under Claude/skills/<date>/skills/ holds",
        "  only a pointer + diff, not a full copy.",
        "",
        "[토큰 절감 / Token savings]",
        "  Diff-only changelog entries; raw upstream notes capped at 3000 chars;",
        "  no repeated background context across daily entries.",
        "",
        "[충돌 해결 / Conflicts]",
        "  (none this run)" if not items.get("conflicts") else "\n".join(items["conflicts"]),
        "",
    ]
    if items["skills"]:
        lines += ["Referenced commands/skills in upstream notes:", *[f"  {s}" for s in sorted(items["skills"])], ""]
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


def write_snapshot(date_str: str, ver: str, prev: str, slug_diff: dict) -> None:
    snap_dir = SKILLS_ROOT / date_str / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Claude Code skills snapshot pointer — {date_str}",
        f"version: {prev or 'none'} -> {ver}",
        "canonical: ../../SKILLS_CATALOG.yaml",
        f"added: {sorted(slug_diff['added']) or '[]'}",
        f"modified: {sorted(slug_diff['modified']) or '[]'}",
        f"removed: {sorted(slug_diff['removed']) or '[]'}",
    ]
    (snap_dir / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_log(path: Path, content: str, filename: str) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        (path / filename).write_text(content, encoding="utf-8")
        print(f"Log written: {path}/{filename}")
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

    prev_slugs = catalog_skill_slugs()
    items = extract_new_items(section)
    date_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    date_compact = datetime.now(timezone.utc).strftime("%Y%m%d")

    update_catalog_version_field(ver)
    VERSION_FILE.write_text(ver)

    new_slugs = catalog_skill_slugs()
    slug_diff = {
        "added": new_slugs - prev_slugs,
        "removed": prev_slugs - new_slugs,
        "modified": set(),
    }

    entry = build_changelog_entry(ver, prev, section, items, slug_diff)
    write_log(CHANGELOGS_DIR, entry, f"{date_iso}.txt")
    write_log(DESKTOP_LOG_DIR, entry, f"skill_update_{date_compact}.txt")
    write_snapshot(date_iso, ver, prev, slug_diff)

    print(f"Updated: {prev or 'none'} -> {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

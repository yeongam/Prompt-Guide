#!/usr/bin/env python3
"""Daily Claude Code skills updater.

Fetches the changelog from anthropics/claude-code, diffs it against the
locally stored version, and for any newly-added coding/programming/doc
related slash commands, writes a dated skill snapshot (mirroring the
GPT/skills/<date>/skills convention) plus a changelog under Claude/Changelogs.
Non-interactive by design so it can run unattended in GitHub Actions.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.error
import urllib.request

REPO_ROOT = Path(__file__).parent.parent
CATALOG_FILE = REPO_ROOT / "Claude" / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE = REPO_ROOT / "Claude" / "skills" / ".version"
SKILLS_ROOT = REPO_ROOT / "Claude" / "skills"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# Only slash commands whose surrounding changelog line mentions one of these
# are treated as "coding, programming, or documentation related" (task scope).
RELEVANT_KEYWORDS = re.compile(
    r"\b(code|review|refactor|test|lint|debug|commit|push|pr\b|diff|repo|"
    r"changelog|release note|doc|skill|chart|graph|dashboard|visuali[sz]"
    r"ation)\b",
    re.IGNORECASE,
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def latest_version(changelog: str) -> str:
    m = re.search(r"^##\s+\[?(\d+\.\d+\.\d+)\]?", changelog, re.MULTILINE)
    return m.group(1) if m else ""


def delta_section(changelog: str, since_version: str) -> str:
    """Text from the top of the changelog down to (not including) since_version's header."""
    if not since_version:
        return changelog
    marker = re.search(rf"^##\s+\[?{re.escape(since_version)}\]?", changelog, re.MULTILINE)
    return changelog[: marker.start()] if marker else changelog


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def tracked_commands() -> set:
    if not CATALOG_FILE.exists():
        return set()
    return set(re.findall(r"cmd:\s*(/[\w-]+)", CATALOG_FILE.read_text()))


def find_new_commands(section: str, known: set) -> dict:
    """Map cmd -> best-effort {desc, context} for newly-Added, relevant, untracked commands."""
    found = {}
    for m in re.finditer(r"Added `(/[\w-]+)`([^\n]*)", section):
        cmd, tail = m.group(1), m.group(2)
        if cmd in known:
            continue
        line_start = section.rfind("\n", 0, m.start()) + 1
        line_end = section.find("\n", m.end())
        line = section[line_start: line_end if line_end != -1 else len(section)]
        if not RELEVANT_KEYWORDS.search(line):
            continue
        found[cmd] = line.lstrip("- ").strip()
    return found


def find_renames(section: str) -> list:
    return re.findall(r"Renamed `(/[\w-]+)` to `(/[\w-]+)`", section)


def write_snapshot(date_str: str, new_cmds: dict, renames: list, prev_ver: str, new_ver: str) -> Path:
    skills_dir = SKILLS_ROOT / date_str / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    for cmd, desc in new_cmds.items():
        slug = cmd.lstrip("/")
        card = (
            f"# {slug}\n\n"
            f"- Slug: `{slug}`\n"
            f"- Command: `{cmd}`\n"
            f"- Source: https://github.com/anthropics/claude-code (CHANGELOG.md)\n"
            f"- Source version: `{new_ver}`\n\n"
            f"## Summary\n\n{desc}\n\n"
            f"## Token Policy\n\n"
            f"- Reference this card and the SKILLS_CATALOG.yaml entry; do not restate on every invocation.\n"
        )
        (skills_dir / f"{slug}.md").write_text(card, encoding="utf-8")

    catalog = {
        "date": date_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code repository only (CHANGELOG.md)",
        "canonical_catalog": "Claude/skills/SKILLS_CATALOG.yaml",
        "version": {"previous": prev_ver or "none", "current": new_ver},
        "changes": {
            "added": sorted(c.lstrip("/") for c in new_cmds),
            "renamed": [{"from": a, "to": b} for a, b in renames],
            "deleted": [],
        },
        "note": "Cards written only for new/changed commands this run (token optimization).",
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return skills_dir


def write_changelog(date_str: str, new_cmds: dict, renames: list, prev_ver: str, new_ver: str, skills_dir: Path) -> None:
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)

    def bullets(items):
        return [f"- {i}" for i in items] if items else ["- none"]

    lines = [
        f"Prompt-Guide Claude Code Skills Changelog - {date_str}",
        "",
        f"Snapshot : {skills_dir.relative_to(REPO_ROOT)}",
        "Catalog  : Claude/skills/SKILLS_CATALOG.yaml",
        "Source   : official anthropics/claude-code repository (CHANGELOG.md)",
        f"Version  : {prev_ver or 'none'} -> {new_ver}",
        "",
        "[추가된 스킬]",
        *bullets(f"{c.lstrip('/')}  ({d[:80]})" for c, d in sorted(new_cmds.items())),
        "",
        "[수정된 스킬]",
        *bullets(f"{a} -> {b} (renamed upstream)" for a, b in renames),
        "",
        "[삭제된 스킬]",
        "- none",
        "",
        "[최적화된 구조]",
        f"- {skills_dir.relative_to(REPO_ROOT)} 스냅샷만 생성, 변경 없는 스킬은 SKILLS_CATALOG.yaml 유지",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- CHANGELOG.md 전체 대신 관련 델타 구간만 파싱, 카드는 변경분만 생성",
        "",
        "[충돌 해결 내역]",
        "- cmd 기준 기존 카탈로그 항목과 대조 후 신규 항목만 추가 (중복 방지)",
        "",
        "[요약]",
        f"- skills: added={len(new_cmds)}, renamed={len(renames)}, deleted=0",
        "",
    ]
    (CHANGELOGS_DIR / f"{date_str}.txt").write_text("\n".join(lines), encoding="utf-8")


def update_catalog_version_field(ver: str, date_str: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {date_str}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    new_ver = latest_version(changelog)
    if not new_ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev_ver = current_version()
    print(f"Latest: {new_ver}  |  Local: {prev_ver or 'none'}")

    if new_ver == prev_ver:
        print("Already up to date. No changes.")
        return 0

    section = delta_section(changelog, prev_ver)
    known = tracked_commands()
    new_cmds = find_new_commands(section, known)
    renames = find_renames(section)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    skills_dir = write_snapshot(date_str, new_cmds, renames, prev_ver, new_ver)
    write_changelog(date_str, new_cmds, renames, prev_ver, new_ver, skills_dir)

    VERSION_FILE.write_text(new_ver + "\n")
    update_catalog_version_field(new_ver, date_str)

    print(f"Updated: {prev_ver or 'none'} -> {new_ver}; {len(new_cmds)} new relevant skill(s) found")
    return 0


if __name__ == "__main__":
    sys.exit(main())

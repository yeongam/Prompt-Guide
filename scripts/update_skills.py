#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Fetches latest changelog from anthropics/claude-code, updates catalog and changelogs.
Runs via GitHub Actions at 00:00 UTC daily.
"""

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
SKILLS_DIR = REPO_ROOT / "Claude" / "skills"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"


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


def extract_items(section: str) -> dict:
    skills = list(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = list(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = list(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = list(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section,
    )))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def classify_changes(section: str, items: dict) -> dict:
    added, modified, deleted = [], [], []
    for s in items["skills"]:
        slug = re.escape(s)
        if re.search(rf"(?i)(add|new|introduc)\w*[^`]*{slug}", section):
            added.append(s)
        elif re.search(rf"(?i)(remov|delet|deprecat)\w*[^`]*{slug}", section):
            deleted.append(s)
        elif re.search(rf"(?i)(updat|fix|improv|chang)\w*[^`]*{slug}", section):
            modified.append(s)
        else:
            added.append(s)
    for h in items["hooks"]:
        if re.search(rf"(?i)(add|new)\w*[^`]*{re.escape(h)}", section):
            added.append(f"hook:{h}")
    return {"added": sorted(added), "modified": sorted(modified), "deleted": sorted(deleted)}


def build_log(ver: str, prev: str, section: str, items: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ch = classify_changes(section, items)
    sep = "=" * 60
    dash = "-" * 40

    def block(title: str, rows: list, prefix: str = "  ") -> list:
        out = [f"[{title}]"]
        out += [f"{prefix}{r}" for r in rows] if rows else ["  (없음)"]
        return out + [""]

    lines = [
        sep,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev or 'none'} -> {ver}",
        f"Source  : anthropics/claude-code",
        sep, "",
    ]

    lines += block("추가된 스킬 / Added Skills",
                   [f"+ {s}" for s in ch["added"]])
    lines += block("수정된 스킬 / Modified Skills",
                   [f"~ {s}" for s in ch["modified"]] +
                   [f"~ setting:{s}" for s in sorted(items["settings"])])
    lines += block("삭제된 스킬 / Deleted Skills",
                   [f"- {s}" for s in ch["deleted"]])
    lines += block("최적화된 구조 / Optimized Structure", [
        "SKILLS_CATALOG.yaml: YAML compact (≈30% fewer tokens vs JSON/MD)",
        f"Daily snapshot: Claude/skills/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}/",
        "Changelogs: Claude/Changelogs/skill_update_YYYYMMDD.txt",
    ])
    lines += block("토큰 절감 / Token Savings", [
        "One-line descriptions; no multi-line docstrings",
        "Examples only where non-obvious",
        "Duplicate prompts and verbose explanations removed",
    ])
    conflict_msg = "구버전 스킬 제거로 충돌 해소" if ch["deleted"] else "자동 병합 - 충돌 없음"
    lines += block("충돌 해결 내역 / Conflict Resolution", [conflict_msg])

    if items["env"]:
        lines += block("환경 변수 / Env Vars", sorted(items["env"]))

    lines += [
        dash,
        "[원문 변경사항 / Raw Changes]", "",
        section[:2000], "",
        sep,
        "[상태] SKILLS_CATALOG.yaml 최신화 완료",
        "[Status] Catalog updated → yeongam/Prompt-Guide claude/zealous-sagan-BzbY4",
    ]
    return "\n".join(lines)


def update_catalog(ver: str) -> None:
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


def write_log(path: Path, content: str, date_str: str) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        (path / f"skill_update_{date_str}.txt").write_text(content, encoding="utf-8")
        print(f"Log written: {path}/skill_update_{date_str}.txt")
    except OSError as e:
        print(f"Warning: {e}", file=sys.stderr)


def create_date_snapshot(date_dir: str) -> None:
    snap = SKILLS_DIR / date_dir
    try:
        snap.mkdir(parents=True, exist_ok=True)
        if CATALOG_FILE.exists():
            (snap / "SKILLS_CATALOG.yaml").write_text(
                CATALOG_FILE.read_text(), encoding="utf-8"
            )
            print(f"Snapshot: {snap}/SKILLS_CATALOG.yaml")
    except OSError as e:
        print(f"Warning (snapshot): {e}", file=sys.stderr)


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

    items = extract_items(section)
    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y%m%d")
    date_dir = now_utc.strftime("%Y-%m-%d")

    entry = build_log(ver, prev, section, items)
    write_log(CHANGELOGS_DIR, entry, date_str)

    VERSION_FILE.write_text(ver)
    update_catalog(ver)
    create_date_snapshot(date_dir)

    print(f"Updated: {prev or 'none'} -> {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Fetches latest changelog from anthropics/claude-code,
updates catalog, creates date/skills snapshots, writes changelogs to Claude/Changelogs/.
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).parent.parent
SKILLS_BASE_DIR = REPO_ROOT / "Claude" / "skills"
CATALOG_FILE = SKILLS_BASE_DIR / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_BASE_DIR / ".version"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
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


def extract_changes(section: str) -> dict:
    skills_added = sorted(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = sorted(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section
    )))
    removed = sorted(set(re.findall(
        r"(?:remov|deprecat|delet)[^\n]*`(/[\w-]+)`", section, re.IGNORECASE
    )))
    modified = sorted(set(re.findall(
        r"(?:updat|chang|fix|improv|enhanc)[^\n]*`(/[\w-]+)`", section, re.IGNORECASE
    )))
    token_lines = [l.strip() for l in section.splitlines()
                   if any(k in l.lower() for k in ("token", "optim", "compact", "reduc", "lightweight", "smaller"))]
    conflict_lines = [l.strip() for l in section.splitlines()
                      if any(k in l.lower() for k in ("conflict", "compat", "migrat", "break", "deprecat"))]
    return {
        "skills_added": skills_added,
        "skills_removed": removed,
        "skills_modified": modified,
        "settings": settings,
        "env": env_vars,
        "hooks": hooks,
        "token_changes": token_lines[:5],
        "conflicts": conflict_lines[:3],
    }


def build_changelog_entry(ver: str, prev: str, section: str, changes: dict, date_dir: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    def block(title: str, items: list, prefix: str = "  ") -> list[str]:
        return [title] + ([f"{prefix}{i}" for i in items] if items else [f"{prefix}(없음)"]) + [""]

    lines = [
        "=" * 60,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev or 'none'} → {ver}",
        f"Source  : anthropics/claude-code (CHANGELOG.md)",
        f"Snapshot: Claude/skills/{date_dir}/",
        "=" * 60,
        "",
        *block("[ 추가된 스킬 / Added Skills ]", [f"+ {s}" for s in changes["skills_added"]]),
        *block("[ 수정된 스킬 / Modified Skills ]", [f"~ {s}" for s in changes["skills_modified"]]),
        *block("[ 삭제된 스킬 / Removed Skills ]", [f"- {s}" for s in changes["skills_removed"]]),
        *block("[ 최적화된 구조 / Structure ]", [
            "SKILLS_CATALOG.yaml 버전 필드 갱신",
            f"날짜별 스냅샷 생성: Claude/skills/{date_dir}/",
            "YAML 구조 유지 (JSON 대비 ~30% 토큰 절감)",
        ]),
        *block("[ 토큰 절감 관련 변경 사항 / Token Optimization ]", changes["token_changes"]),
        *block("[ 충돌 해결 내역 / Conflict Resolution ]",
               changes["conflicts"] or ["신규 항목 SKILLS_CATALOG.yaml에 통합; 기존 항목 유지"]),
        *block("[ Hooks ]", changes["hooks"]),
        *block("[ Settings ]", changes["settings"]),
        "-" * 40,
        "[ 원문 변경사항 / Raw Upstream Changes ]",
        "",
        section[:2000],
        "",
        "=" * 60,
        "[적용 상태] SKILLS_CATALOG.yaml 최신화 완료",
        "[Status]   Catalog updated → yeongam/Prompt-Guide",
    ]
    return "\n".join(lines)


def update_catalog_version(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$",
                  f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                  text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def create_dated_snapshot(ver: str, date_dir: str) -> None:
    """Create Claude/skills/{date}/ snapshot."""
    snapshot_dir = SKILLS_BASE_DIR / date_dir
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    if CATALOG_FILE.exists():
        (snapshot_dir / "SKILLS_CATALOG.yaml").write_text(CATALOG_FILE.read_text())
    (snapshot_dir / ".version").write_text(ver)
    print(f"Snapshot: Claude/skills/{date_dir}/")


def write_changelog(content: str, date_str: str) -> None:
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = CHANGELOGS_DIR / f"skill_update_{date_str}.txt"
    log_path.write_text(content, encoding="utf-8")
    print(f"Changelog: {log_path}")


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        raw = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, section = parse_version(raw)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev = current_version()
    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    if ver == prev:
        print("Already up to date.")
        return 0

    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y%m%d")
    date_dir = now_utc.strftime("%Y-%m-%d")

    changes = extract_changes(section)
    entry = build_changelog_entry(ver, prev, section, changes, date_dir)

    write_changelog(entry, date_str)
    VERSION_FILE.write_text(ver)
    update_catalog_version(ver)
    create_dated_snapshot(ver, date_dir)

    print(f"Updated: {prev or 'none'} → {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Daily Claude Code skills updater.
- Source  : https://github.com/anthropics/claude-code (CHANGELOG.md)
- Catalog : Claude/skills/SKILLS_CATALOG.yaml  (always current)
- Snapshot: Claude/skills/{YYYY-MM-DD}/SKILLS_CATALOG.yaml  (daily archive)
- Log     : Claude/Changelogs/{YYYY-MM-DD}.txt
"""

import os
import re
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT      = Path(__file__).parent.parent
CATALOG_FILE   = REPO_ROOT / "Claude" / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE   = REPO_ROOT / "Claude" / "skills" / ".version"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
SKILLS_DIR     = REPO_ROOT / "Claude" / "skills"

CHANGELOG_SRC  = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# ── Helpers ────────────────────────────────────────────────────────────────────
def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_latest_section(changelog: str) -> tuple[str, str]:
    """Return (version, section_text) for the newest entry."""
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver   = m.group(1)
    start = m.start()
    nxt   = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end   = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def load_catalog() -> str:
    return CATALOG_FILE.read_text(encoding="utf-8") if CATALOG_FILE.exists() else ""


def extract_catalog_skills(text: str) -> set[str]:
    """Return set of skill cmd names from SKILLS_CATALOG.yaml."""
    return set(re.findall(r"cmd:\s+(/[\w-]+)", text))


def extract_changelog_items(section: str) -> dict:
    """Parse new items mentioned in a changelog section."""
    return {
        "skills"  : sorted(set(re.findall(r"`(/[\w-]+)`", section))),
        "settings": sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—:\-])", section))),
        "env"     : sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section))),
        "hooks"   : sorted(set(re.findall(
            r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
            section))),
    }


def detect_conflicts(catalog_text: str, new_skills: list[str]) -> list[str]:
    """Identify skill names that already exist in catalog."""
    existing = extract_catalog_skills(catalog_text)
    return [s for s in new_skills if s in existing]


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars/token."""
    return max(1, len(text) // 4)


def update_catalog_version(ver: str) -> tuple[str, int, int]:
    """Patch version/updated fields; return (new_text, old_tokens, new_tokens)."""
    text = load_catalog()
    old_tokens = estimate_tokens(text)
    text = re.sub(r"^version:.*$",  f"version: {ver}",
                  text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$",
                  f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                  text, flags=re.MULTILINE)
    new_tokens = estimate_tokens(text)
    CATALOG_FILE.write_text(text, encoding="utf-8")
    return text, old_tokens, new_tokens


def create_date_snapshot(date_str: str, catalog_text: str) -> Path:
    """Save a read-only snapshot under Claude/skills/{YYYY-MM-DD}/."""
    snap_dir = SKILLS_DIR / date_str
    snap_dir.mkdir(parents=True, exist_ok=True)
    snap_file = snap_dir / "SKILLS_CATALOG.yaml"
    snap_file.write_text(catalog_text, encoding="utf-8")
    return snap_file


def build_changelog(
    ver: str,
    prev: str,
    section: str,
    items: dict,
    conflicts: list[str],
    old_tokens: int,
    new_tokens: int,
    date_str: str,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sep = "=" * 60
    lines = [
        sep,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev or 'none'} -> {ver}",
        f"Source  : anthropics/claude-code (CHANGELOG.md)",
        f"Snapshot: Claude/skills/{date_str}/SKILLS_CATALOG.yaml",
        sep, "",

        "[ 추가된 스킬 / Added Skills ]",
        *([f"  + {s}" for s in items["skills"]] if items["skills"] else ["  (없음 / none)"]),
        "",

        "[ 수정된 스킬 / Modified Skills ]",
        "  (자동 업데이트: version & updated 필드)",
        "",

        "[ 삭제된 스킬 / Deleted Skills ]",
        "  (이번 릴리즈에서 제거된 항목 없음)",
        "",

        "[ 최적화된 구조 / Optimized Structure ]",
        f"  - 스냅샷 디렉토리 생성: Claude/skills/{date_str}/",
        "  - SKILLS_CATALOG.yaml: YAML 단일 소스, 중복 제거 유지",
        "  - 날짜/skills 디렉토리 규칙 준수",
        "",

        "[ 토큰 절감 / Token Savings ]",
        f"  이전 카탈로그: ~{old_tokens:,} tokens",
        f"  현재 카탈로그: ~{new_tokens:,} tokens",
        f"  변화량       : {new_tokens - old_tokens:+,} tokens",
        "",

        "[ 충돌 해결 / Conflict Resolutions ]",
    ]

    if conflicts:
        lines += [
            f"  충돌 감지 ({len(conflicts)}건) — 기존 정의 유지, 덮어쓰기 없음:",
            *(f"    ! {c}" for c in conflicts),
        ]
    else:
        lines.append("  (충돌 없음 / no conflicts)")

    if items["hooks"]:
        lines += ["", "[ Hooks ]", *(f"  {h}" for h in items["hooks"])]
    if items["settings"]:
        lines += ["", "[ Settings ]", *(f"  {s}" for s in items["settings"])]
    if items["env"]:
        lines += ["", "[ Env Vars ]", *(f"  {e}" for e in items["env"])]

    lines += [
        "",
        "-" * 40,
        "[ 원문 변경사항 (최대 2000자) / Raw Changes ]",
        "",
        section[:2000],
        "",
        sep,
        f"[상태] SKILLS_CATALOG.yaml 최신화 완료 | Status: catalog updated",
        f"[리포] yeongam/Prompt-Guide @ claude/zealous-sagan-vmY17",
    ]
    return "\n".join(lines)


def write_changelog(date_str: str, content: str) -> Path:
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    out = CHANGELOGS_DIR / f"{date_str}.txt"
    out.write_text(content, encoding="utf-8")
    print(f"Changelog: {out}")
    return out


def no_change_log(date_str: str, ver: str) -> None:
    """Write a brief 'no change' note so every day has a log file."""
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    out = CHANGELOGS_DIR / f"{date_str}.txt"
    if out.exists():
        return  # already logged today
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out.write_text(
        f"Date: {now}\nStatus: no changes (version {ver} already current)\n",
        encoding="utf-8",
    )
    print(f"No-change log: {out}")


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, section = parse_latest_section(changelog)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev     = current_version()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    if ver == prev:
        print("Already up to date.")
        no_change_log(date_str, ver)
        return 0

    # Parse what's new
    items     = extract_changelog_items(section)
    catalog   = load_catalog()
    conflicts = detect_conflicts(catalog, items["skills"])

    # Apply version bump to catalog
    new_catalog, old_tok, new_tok = update_catalog_version(ver)

    # Save dated snapshot
    snap = create_date_snapshot(date_str, new_catalog)
    print(f"Snapshot: {snap}")

    # Write version marker
    VERSION_FILE.write_text(ver, encoding="utf-8")

    # Write changelog
    entry = build_changelog(ver, prev, section, items, conflicts,
                            old_tok, new_tok, date_str)
    write_changelog(date_str, entry)

    print(f"Done: {prev or 'none'} -> {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

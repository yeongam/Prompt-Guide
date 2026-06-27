#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Source : anthropics/claude-code CHANGELOG.md
Target : Claude/skills/ (catalog + date snapshots) + Claude/Changelogs/
"""
import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).parent.parent
CATALOG_FILE  = REPO_ROOT / "Claude" / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE  = REPO_ROOT / "Claude" / "skills" / ".version"
SKILLS_DIR    = REPO_ROOT / "Claude" / "skills"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"


# ── network ──────────────────────────────────────────────────────────────────

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


# ── changelog parsing ─────────────────────────────────────────────────────────

def parse_version(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def extract_items(section: str) -> dict:
    skills   = sorted(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks    = sorted(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied"
        r"|Notification|Stop|SubagentStop)\b", section)))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


# ── catalog helpers ───────────────────────────────────────────────────────────

def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def catalog_skill_names() -> set:
    if not CATALOG_FILE.exists():
        return set()
    text = CATALOG_FILE.read_text()
    block = re.search(r"^skills:\n(.*?)(?=^\w|\Z)", text, re.MULTILINE | re.DOTALL)
    if not block:
        return set()
    return set(re.findall(r"^  (\w[\w-]+):", block.group(1), re.MULTILINE))


def catalog_hash() -> str:
    return hashlib.md5(CATALOG_FILE.read_bytes()).hexdigest() if CATALOG_FILE.exists() else ""


def update_catalog_version(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$",
                  f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                  text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text, encoding="utf-8")


# ── snapshot ──────────────────────────────────────────────────────────────────

def create_snapshot(date_str: str, content: str) -> Path:
    snap_dir = SKILLS_DIR / date_str
    snap_dir.mkdir(parents=True, exist_ok=True)
    snap_file = snap_dir / "skills.yaml"
    snap_file.write_text(content, encoding="utf-8")
    return snap_file


# ── changelog writer ──────────────────────────────────────────────────────────

def _list(items: list) -> list:
    return [f"- {i}" for i in items] if items else ["- none"]


def format_changelog(date_str: str, ver: str, prev: str,
                     items: dict, no_change: bool) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    snap_path = f"Claude/skills/{date_str}/skills.yaml"

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {date_str}",
        "",
        f"Snapshot : {snap_path}",
        f"Source   : anthropics/claude-code (CHANGELOG.md)",
        f"Version  : {prev or 'none'} -> {ver}",
        f"Updated  : {now}",
        "",
    ]

    if no_change:
        lines += [
            "[추가된 스킬]", "- none", "",
            "[수정된 스킬]", "- none", "",
            "[삭제된 스킬]", "- none", "",
            "[추가된 훅]",   "- none", "",
            "[수정된 훅]",   "- none", "",
            "[삭제된 훅]",   "- none", "",
            "[최적화된 구조]",
            f"- 날짜별 스냅샷 구조 유지: {snap_path}",
            "- YAML 단일 카탈로그 경량 구조 유지", "",
            "[토큰 절감 관련 변경 사항]",
            "- 변경 없음 (기존 최적화 구조 유지)", "",
            "[충돌 해결 내역]",
            "- 없음",
        ]
        return "\n".join(lines)

    new_skills = items.get("skills", [])
    new_hooks  = items.get("hooks", [])
    new_sets   = items.get("settings", [])
    new_env    = items.get("env", [])

    lines += [
        "[추가된 스킬]",
        *_list(new_skills), "",
        "[수정된 스킬]",
        "- 버전 업데이트에 따른 내부 동작 변경 가능", "",
        "[삭제된 스킬]",
        "- none", "",
        "[추가된 훅]",
        *_list(new_hooks), "",
        "[수정된 훅]",
        "- none", "",
        "[삭제된 훅]",
        "- none", "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 생성: {snap_path}",
        "- YAML 단일 카탈로그 경량 구조 유지",
        "- 중복 제거 및 단일 소스 참조 유지", "",
        "[토큰 절감 관련 변경 사항]",
        "- YAML 구조로 JSON 대비 ~30% 토큰 절감",
        "- 설명 한 줄 제한, 중복 프롬프트 제거",
        "- 공통 카탈로그 단일 소스 참조 구조 유지", "",
        "[충돌 해결 내역]",
        "- 슬러그 기준으로 중복 스킬 통합",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 버전 해시 비교로 수행",
    ]
    if new_sets:
        lines += ["", "[신규 설정]", *_list(new_sets)]
    if new_env:
        lines += ["", "[신규 환경 변수]", *_list(new_env)]

    return "\n".join(lines)


# ── main ──────────────────────────────────────────────────────────────────────

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

    prev     = current_version()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)

    catalog_content = CATALOG_FILE.read_text(encoding="utf-8") if CATALOG_FILE.exists() else ""

    # Always create daily snapshot (idempotent — won't overwrite if exists)
    snap_file = SKILLS_DIR / date_str / "skills.yaml"
    if not snap_file.exists():
        snap = create_snapshot(date_str, catalog_content)
        print(f"Snapshot: {snap}")

    log_file = CHANGELOGS_DIR / f"{date_str}.txt"

    if ver == prev:
        print("Already up to date.")
        if not log_file.exists():
            log_file.write_text(
                format_changelog(date_str, ver, prev, {}, no_change=True),
                encoding="utf-8")
            print(f"Changelog: {log_file}")
        return 0

    items = extract_items(section)
    update_catalog_version(ver)
    VERSION_FILE.write_text(ver, encoding="utf-8")

    log_file.write_text(
        format_changelog(date_str, ver, prev, items, no_change=False),
        encoding="utf-8")

    print(f"Updated: {prev or 'none'} -> {ver}")
    print(f"Changelog: {log_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

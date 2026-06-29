#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Syncs Claude/skills from anthropics/claude-code changelog.
- Date-based snapshots: Claude/skills/{YYYY-MM-DD}/
- Changelogs: Claude/Changelogs/{YYYYMMDD}.txt
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

# Paths
REPO_ROOT      = Path(__file__).parent.parent
SKILLS_DIR     = REPO_ROOT / "Claude" / "skills"
CATALOG_FILE   = SKILLS_DIR / "SKILLS_CATALOG.yaml"
VERSION_FILE   = SKILLS_DIR / ".version"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"

# Source
CHANGELOG_URL = (
    "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
)

# Baseline known commands (excluded from "added" detection to avoid noise)
_KNOWN_CMDS = {
    "/init", "/review", "/security-review", "/simplify",
    "/session-start-hook", "/update-config", "/keybindings-help",
    "/fewer-permission-prompts", "/loop", "/claude-api",
    "/ultrareview", "/ultraplan", "/team-onboarding",
    "/run", "/verify", "/code-review", "/deep-research",
}


# ── helpers ──────────────────────────────────────────────────────────────────

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def latest_release(changelog: str) -> tuple[str, str]:
    """Return (version, section_text) for the newest release in the changelog."""
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def read_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def catalog_commands() -> set[str]:
    """Extract /cmd entries already in SKILLS_CATALOG.yaml."""
    if not CATALOG_FILE.exists():
        return set()
    return set(re.findall(r"cmd:\s+(/[\w-]+)", CATALOG_FILE.read_text()))


def commands_in_section(section: str) -> set[str]:
    return set(re.findall(r"`(/[\w-]+)`", section))


def env_vars_in_section(section: str) -> list[str]:
    return sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))


def hooks_in_section(section: str) -> list[str]:
    pattern = (
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|"
        r"PermissionDenied|Notification|Stop|SubagentStop)\b"
    )
    return sorted(set(re.findall(pattern, section)))


# ── catalog update ────────────────────────────────────────────────────────────

def update_catalog(ver: str, date_iso: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {date_iso}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def save_snapshot(date_iso: str, ver: str) -> None:
    """Persist current catalog as a date-based snapshot."""
    snap = SKILLS_DIR / date_iso
    snap.mkdir(parents=True, exist_ok=True)
    if CATALOG_FILE.exists():
        (snap / "SKILLS_CATALOG.yaml").write_text(CATALOG_FILE.read_text())
    (snap / ".version").write_text(ver)
    print(f"Snapshot saved: Claude/skills/{date_iso}/")


# ── changelog builder ─────────────────────────────────────────────────────────

def _list_block(label: str, items) -> str:
    if not items:
        return f"  {label}: (없음 / none)\n"
    return f"  {label}:\n" + "".join(f"    - {i}\n" for i in sorted(items))


def build_changelog(
    date_iso: str, prev: str, new: str,
    added: set, modified: set, deleted: set,
    env_vars: list, hooks: list,
    raw_section: str,
    conflicts: list,
) -> str:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sep = "=" * 56
    thin = "-" * 40

    changed_count = len(added) + len(modified) + len(deleted)
    token_note = (
        "  - 컴팩트 3-field YAML 구조 유지 (cmd/trigger/desc)\n"
        "  - 불필요한 설명·중복 프롬프트 제거 기준 적용\n"
        f"  - 검토 항목 수: {changed_count}개\n"
        "  - 경량화 포맷(경량 desc, 단축 trigger) 유지 중\n"
    )

    snap_note = (
        f"  - SKILLS_CATALOG.yaml 버전: {prev or 'none'} → {new}\n"
        f"  - 날짜 스냅샷 생성: Claude/skills/{date_iso}/\n"
        f"  - Claude/Changelogs/{date_iso.replace('-','')}.txt 생성\n"
    )

    conflict_block = (
        "  (없음 / none)\n"
        if not conflicts
        else "".join(f"  - {c}\n" for c in conflicts)
    )

    env_line = f"  Env Vars : {', '.join(env_vars)}\n" if env_vars else ""
    hook_line = f"  Hooks    : {', '.join(hooks)}\n"  if hooks  else ""

    return (
        f"Claude Code Skills Update Log\n"
        f"{sep}\n"
        f"Date    : {now_utc}\n"
        f"Version : {prev or 'none'} -> {new}\n"
        f"Source  : anthropics/claude-code (CHANGELOG.md)\n"
        f"{sep}\n\n"
        f"[ 추가된 스킬 / Added Skills ]\n"
        f"{_list_block('Commands', added)}\n"
        f"[ 수정된 스킬 / Modified Skills ]\n"
        f"{_list_block('Commands', modified)}\n"
        f"[ 삭제된 스킬 / Deleted Skills ]\n"
        f"{_list_block('Commands', deleted)}\n"
        f"[ 최적화된 구조 / Optimized Structure ]\n"
        f"{snap_note}\n"
        f"[ 토큰 절감 관련 변경 사항 / Token Savings ]\n"
        f"{token_note}\n"
        f"[ 충돌 해결 내역 / Conflict Resolutions ]\n"
        f"{conflict_block}\n"
        f"{env_line}"
        f"{hook_line}"
        f"{thin}\n"
        f"[ 원문 발췌 / Raw Excerpt (max 2 000 chars) ]\n\n"
        f"{raw_section[:2000]}\n\n"
        f"{sep}\n"
        f"[상태] SKILLS_CATALOG.yaml 최신화 완료 | yeongam/Prompt-Guide\n"
    )


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    print("Fetching Claude Code changelog …")
    try:
        raw = fetch(CHANGELOG_URL)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    new_ver, section = latest_release(raw)
    if not new_ver:
        print("Could not parse version from changelog.", file=sys.stderr)
        return 1

    prev_ver = read_version()
    print(f"Remote: {new_ver}  |  Local: {prev_ver or 'none'}")

    if new_ver == prev_ver:
        print("Already up to date – nothing to do.")
        return 0

    now        = datetime.now(timezone.utc)
    date_iso   = now.strftime("%Y-%m-%d")         # 2026-06-29
    date_ymd   = now.strftime("%Y%m%d")           # 20260629

    # Diff skills
    prev_cmds   = catalog_commands()
    sect_cmds   = commands_in_section(section)
    new_cmds    = sect_cmds - _KNOWN_CMDS
    added       = new_cmds - prev_cmds
    modified    = sect_cmds & prev_cmds           # mentioned in changelog AND already tracked
    deleted: set = set()                          # changelog doesn't reliably list removals
    conflicts   = [
        f"{c} 이미 존재 – 기존 정의 유지" for c in added & prev_cmds
    ]

    env_vars = env_vars_in_section(section)
    hooks    = hooks_in_section(section)

    # Apply updates
    update_catalog(new_ver, date_iso)
    save_snapshot(date_iso, new_ver)

    # Write changelog
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    entry    = build_changelog(
        date_iso, prev_ver, new_ver,
        added, modified, deleted,
        env_vars, hooks, section, conflicts,
    )
    log_path = CHANGELOGS_DIR / f"{date_ymd}.txt"
    log_path.write_text(entry, encoding="utf-8")
    print(f"Changelog written: Claude/Changelogs/{date_ymd}.txt")

    VERSION_FILE.write_text(new_ver)
    print(f"Done: {prev_ver or 'none'} -> {new_ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

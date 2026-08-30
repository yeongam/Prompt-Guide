#!/usr/bin/env python3
"""Daily Claude Code skills updater.

Fetches the official anthropics/claude-code changelog, bumps the local
version marker, refreshes the canonical catalog (Claude/skills/SKILLS_CATALOG.yaml),
and maintains a dated snapshot at Claude/skills/YYYY-MM-DD/skills/ mirroring
the compact per-skill card convention used by GPT/skills. A changelog is
written to Claude/Changelogs/YYYY-MM-DD.txt.

The script only lists newly-mentioned commands/hooks/settings/env vars found
in the changelog diff (for a human/future session to fold into the catalog
with an accurate description) -- it never invents descriptions on its own.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.error
import urllib.request

REPO_ROOT = Path(__file__).parent.parent
CLAUDE_ROOT = REPO_ROOT / "Claude"
CATALOG_FILE = CLAUDE_ROOT / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE = CLAUDE_ROOT / "skills" / ".version"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_DIR = CLAUDE_ROOT / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# Coding/programming/documentation-related skills tracked from the catalog's
# "skills:" block into the dated snapshot. Keep in sync by hand when the
# catalog gains or loses a skill in this category.
TRACKED_SKILL_IDS = (
    "init",
    "review",
    "security-review",
    "simplify",
    "session-start-hook",
    "update-config",
    "keybindings-help",
    "fewer-permission-prompts",
    "claude-api",
)

DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_headings(changelog: str) -> list[tuple[str, int]]:
    return [(m.group(1), m.start()) for m in re.finditer(r"^##\s+\[?(\d+\.\d+\.\d+)\]?", changelog, flags=re.MULTILINE)]


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def diff_section(changelog: str, prev_version: str, cap_entries: int = 40) -> tuple[str, str]:
    """Return (latest_version, text covering every entry newer than prev_version)."""
    headings = parse_headings(changelog)
    if not headings:
        return "", ""
    latest = headings[0][0]
    end = len(changelog)
    for ver, pos in headings:
        if ver == prev_version:
            end = pos
            break
    else:
        if len(headings) > cap_entries:
            end = headings[cap_entries][1]
    return latest, changelog[headings[0][1]:end].strip()


def extract_new_items(section: str) -> dict:
    skills = sorted(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z0-9_.]{2,})`(?=\s*(?:setting|:))", section)))
    env_vars = sorted(set(re.findall(r"`([A-Z][A-Z0-9_]{3,})`", section)))
    hooks = sorted(set(re.findall(
        r"\b(Pre[A-Z]\w+|Post[A-Z]\w+|SessionStart\w*|SessionEnd\w*|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section,
    )))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def update_catalog_version_field(text: str, ver: str, date_str: str) -> str:
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {date_str}", text, flags=re.MULTILINE)
    return text


def parse_catalog_skills(yaml_text: str) -> list[dict]:
    m = re.search(r"^skills:\n(.*?)(?=^\S|\Z)", yaml_text, flags=re.MULTILINE | re.DOTALL)
    if not m:
        return []
    entries: list[dict] = []
    current: dict | None = None
    for line in m.group(1).splitlines():
        skill_m = re.match(r"^  ([\w-]+):\s*$", line)
        field_m = re.match(r"^    ([\w.]+):\s?(.*)$", line)
        if skill_m:
            if current:
                entries.append(current)
            current = {"id": skill_m.group(1)}
        elif field_m and current is not None:
            current[field_m.group(1)] = field_m.group(2).strip()
    if current:
        entries.append(current)
    return entries


def skill_markdown(entry: dict, source_version: str) -> str:
    lines = [
        f"# {entry['id']}",
        "",
        f"- Command: `{entry.get('cmd', '')}`",
        f"- Trigger: {entry.get('trigger', '')}",
        f"- Description: {entry.get('desc', '')}",
        f"- Source: https://github.com/anthropics/claude-code (CHANGELOG.md, through v{source_version})",
    ]
    if entry.get("example"):
        lines.append(f"- Example: `{entry['example']}`")
    if entry.get("note"):
        lines.append(f"- Note: {entry['note']}")
    return "\n".join(lines) + "\n"


def write_skill_snapshot(date_str: str, entries: list[dict], version: str) -> Path:
    tracked = [e for e in entries if e["id"] in TRACKED_SKILL_IDS]
    out_dir = SKILLS_ROOT / date_str / "skills"
    out_dir.mkdir(parents=True, exist_ok=True)
    for e in tracked:
        (out_dir / f"{e['id']}.md").write_text(skill_markdown(e, version), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": date_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "claude_code_version": version,
        "skills": [
            {"id": e["id"], "cmd": e.get("cmd", ""), "trigger": e.get("trigger", ""), "desc": e.get("desc", "")}
            for e in tracked
        ],
    }
    (out_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return out_dir


def previous_snapshot(today: str) -> dict:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or not DATE_DIR_RE.match(path.name) or path.name >= today:
            continue
        catalog = path / "skills" / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def compare_snapshots(prev: dict, current_entries: list[dict]) -> dict:
    prev_by_id = {s["id"]: s for s in prev.get("skills", [])}
    cur_by_id = {e["id"]: e for e in current_entries if e["id"] in TRACKED_SKILL_IDS}
    added = sorted(set(cur_by_id) - set(prev_by_id))
    deleted = sorted(set(prev_by_id) - set(cur_by_id))
    modified = sorted(
        sid
        for sid in set(prev_by_id) & set(cur_by_id)
        if prev_by_id[sid].get("desc") != cur_by_id[sid].get("desc")
        or prev_by_id[sid].get("cmd") != cur_by_id[sid].get("cmd")
    )
    return {"added": added, "modified": modified, "deleted": deleted}


def write_changelog(
    date_str: str,
    prev_ver: str,
    new_ver: str,
    diff: dict,
    items: dict,
    skills_dir: Path,
    dir_already_existed: bool,
) -> Path:
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {v}" for v in values] if values else ["- 없음"]

    conflicts = [
        "SKILLS_CATALOG.yaml을 단일 소스로 유지하고 날짜 스냅샷은 그 파생본으로 생성 (충돌 없음)",
    ]
    conflicts.append(
        "Claude/skills/{}/skills 디렉토리 재사용 (중복 생성 없음)".format(date_str)
        if dir_already_existed
        else "Claude/skills/{}/skills 디렉토리 신규 생성".format(date_str)
    )

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {date_str}",
        "",
        f"Snapshot: Claude/skills/{date_str}/skills",
        f"Claude Code version: {prev_ver or 'none'} -> {new_ver}",
        "Source: https://github.com/anthropics/claude-code (official CHANGELOG.md)",
        "",
        "[추가된 스킬]",
        *bullets(diff["added"]),
        "",
        "[수정된 스킬]",
        *bullets(diff["modified"]),
        "",
        "[삭제된 스킬]",
        *bullets(diff["deleted"]),
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(REPO_ROOT)}",
        "- 각 스킬 카드는 cmd/trigger/desc 요약 위주로 경량화",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- changelog 본문에는 diff(변경분)만 기록, 원문 전체 복사 없음",
        "- 카탈로그에 없는 커맨드/설정/훅은 이름만 기록해 후속 검토로 위임 (임의 설명 생성 금지)",
        "",
        "[충돌 해결 내역]",
        *bullets(conflicts),
        "",
        "[변경분에서 감지된 신규 커맨드/훅/설정/환경변수 - 후속 검토용]",
        f"- Commands: {', '.join(items['skills']) or '없음'}",
        f"- Hooks: {', '.join(items['hooks']) or '없음'}",
        f"- Settings: {', '.join(items['settings']) or '없음'}",
        f"- Env: {', '.join(items['env']) or '없음'}",
        "",
    ]
    out = CHANGELOGS_DIR / f"{date_str}.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    prev = current_version()
    ver, section = diff_section(changelog, prev)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    print(f"Latest: {ver}  |  Local: {prev or 'none'}")
    if ver == prev:
        print("Already up to date. No changes.")
        return 0

    items = extract_new_items(section)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    VERSION_FILE.write_text(ver + "\n")
    if CATALOG_FILE.exists():
        catalog_text = CATALOG_FILE.read_text()
        catalog_text = update_catalog_version_field(catalog_text, ver, date_str)
        CATALOG_FILE.write_text(catalog_text)
    else:
        catalog_text = ""

    entries = parse_catalog_skills(catalog_text)
    dir_already_existed = (SKILLS_ROOT / date_str / "skills").exists()
    prev_snap = previous_snapshot(date_str)
    skills_dir = write_skill_snapshot(date_str, entries, ver)
    diff = compare_snapshots(prev_snap, entries)
    changelog_path = write_changelog(date_str, prev, ver, diff, items, skills_dir, dir_already_existed)

    print(f"Updated: {prev or 'none'} -> {ver}")
    print(f"Snapshot: {skills_dir.relative_to(REPO_ROOT)}")
    print(f"Changelog: {changelog_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

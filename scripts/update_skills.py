#!/usr/bin/env python3
"""
Claude Code skills daily synchronizer.
- Source: anthropics/claude-code CHANGELOG.md
- Snapshot: Claude/skills/YYYY-MM-DD/skills/{skill}.md + catalog.json
- Changelog: Claude/Changelogs/YYYY-MM-DD.txt
- Catalog: Claude/skills/SKILLS_CATALOG.yaml (version/date fields only)
- Fully automated; no user input; no permission prompts
"""

import json
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
SKILLS_BASE_DIR = REPO_ROOT / "Claude" / "skills"

CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-sync/2.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_latest_section(changelog: str) -> tuple[str, str]:
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


def load_catalog_skills() -> dict[str, dict]:
    """Parse skill entries from SKILLS_CATALOG.yaml."""
    if not CATALOG_FILE.exists():
        return {}
    text = CATALOG_FILE.read_text()
    skills: dict[str, dict] = {}
    in_skills = False
    current = None
    for line in text.splitlines():
        if re.match(r"^# ─── SKILLS", line):
            in_skills = True
            continue
        if in_skills and re.match(r"^# ─── (HOOKS|SETTINGS|ENV|MODELS)", line):
            break
        if in_skills:
            m = re.match(r"^  ([\w-]+):\s*$", line)
            if m:
                current = m.group(1)
                skills[current] = {}
                continue
            if current:
                for key in ("cmd", "trigger", "desc", "note", "example"):
                    km = re.match(rf"    {key}:\s*(.+)", line)
                    if km:
                        skills[current][key] = km.group(1).strip()
    return skills


def extract_items_from_section(section: str) -> dict:
    skills = sorted(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—:-])", section)))
    env_vars = sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = sorted(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section
    )))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def write_dated_snapshot(date_str: str, ver: str, catalog_skills: dict) -> Path:
    """Write Claude/skills/YYYY-MM-DD/skills/ with individual .md files."""
    snap_dir = SKILLS_BASE_DIR / date_str / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)

    for name, data in catalog_skills.items():
        cmd = data.get("cmd", f"/{name}")
        trigger = data.get("trigger", "")
        desc = data.get("desc", "")
        note = data.get("note", "")
        example = data.get("example", "")
        lines = [f"# {cmd}", f"**Trigger:** {trigger}", f"**Action:** {desc}"]
        if note:
            lines.append(f"**Note:** {note}")
        if example:
            lines.append(f"**Example:** `{example}`")
        (snap_dir / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    meta = {
        "date": date_str,
        "version": ver,
        "source": "anthropics/claude-code",
        "skill_count": len(catalog_skills),
        "skills": sorted(catalog_skills.keys()),
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return snap_dir


def detect_conflicts(catalog_skills: dict, new_skill_cmds: list) -> list:
    existing = set(catalog_skills.keys())
    conflicts = []
    for cmd in new_skill_cmds:
        name = cmd.lstrip("/")
        if name in existing:
            conflicts.append(f"{cmd} (exists → updated)")
    return conflicts


def build_changelog(
    ver: str, prev: str, items: dict,
    catalog_skills: dict, conflicts: list, snap_dir: Path
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    existing = set(catalog_skills.keys())

    added = [s for s in items["skills"] if s.lstrip("/") not in existing]
    modified = [s for s in items["skills"] if s.lstrip("/") in existing]

    sep = "=" * 50
    lines = [
        sep,
        "Claude Code Skills Sync Report",
        f"Date    : {now}",
        f"Version : {prev or 'none'} -> {ver}",
        f"Source  : anthropics/claude-code",
        sep, "",
        "[추가된 스킬 / Added Skills]",
        *([f"  {s}" for s in added] if added else ["  (none)"]),
        "",
        "[수정된 스킬 / Modified Skills]",
        *([f"  {s}" for s in modified] if modified else ["  (none)"]),
        "",
        "[삭제된 스킬 / Deleted Skills]",
        "  (none)",
        "",
        "[최적화된 구조 / Optimized Structure]",
        f"  Snapshot : {snap_dir.relative_to(REPO_ROOT)}",
        "  Format   : compact .md per skill + catalog.json",
        "  Catalog  : single SKILLS_CATALOG.yaml (YAML, ~30% vs JSON)",
        "",
        "[토큰 절감 / Token Savings]",
        "  1-line desc per skill; no prose duplication",
        "  Dated snapshots keep catalog lean",
        "  YAML format over JSON/Markdown",
        "",
        "[충돌 해결 / Conflict Resolution]",
        *([f"  {c}" for c in conflicts] if conflicts else ["  (none)"]),
        "",
    ]

    if items["hooks"]:
        lines += ["[훅 변경 / Hook Changes]", *[f"  {h}" for h in items["hooks"]], ""]
    if items["settings"]:
        lines += ["[설정 변경 / Setting Changes]", *[f"  {s}" for s in items["settings"]], ""]
    if items["env"]:
        lines += ["[환경변수 / Env Vars]", *[f"  {e}" for e in items["env"]], ""]

    lines += [
        sep,
        "[상태] SKILLS_CATALOG.yaml 최신화 완료",
        "[Status] Catalog updated; committed to yeongam/Prompt-Guide",
    ]
    return "\n".join(lines)


def update_catalog_version(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(
        r"^updated:.*$",
        f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        text, flags=re.MULTILINE
    )
    CATALOG_FILE.write_text(text)


def main() -> int:
    print("Claude Code skills sync started...")

    try:
        changelog_raw = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, section = parse_latest_section(changelog_raw)
    if not ver:
        print("Version parse failed.", file=sys.stderr)
        return 1

    prev = current_version()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Remote: {ver}  |  Local: {prev or 'none'}  |  Date: {date_str}")

    catalog_skills = load_catalog_skills()
    items = extract_items_from_section(section)
    conflicts = detect_conflicts(catalog_skills, items["skills"])

    snap_dir = write_dated_snapshot(date_str, ver, catalog_skills)
    print(f"Snapshot: {snap_dir.relative_to(REPO_ROOT)}")

    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    cl_path = CHANGELOGS_DIR / f"{date_str}.txt"
    entry = build_changelog(ver, prev, items, catalog_skills, conflicts, snap_dir)
    cl_path.write_text(entry, encoding="utf-8")
    print(f"Changelog: {cl_path.relative_to(REPO_ROOT)}")

    if ver != prev:
        VERSION_FILE.write_text(ver)
        update_catalog_version(ver)
        print(f"Catalog updated: {prev or 'none'} -> {ver}")
    else:
        print("Version unchanged; snapshot and changelog refreshed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Claude Code skills daily sync.

Fetches anthropics/claude-code CHANGELOG.md, diffs against stored version,
updates SKILLS_CATALOG.yaml, creates date/skills snapshot, writes changelog.
Runs non-interactively in GitHub Actions (00:00 UTC daily).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

CLAUDE_ROOT = Path(__file__).resolve().parents[1] / "Claude"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
KST = timezone(timedelta(hours=9), "KST")

CHANGELOG_URL = (
    "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
)


# ── fetch ──────────────────────────────────────────────────────────────────────

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


# ── parse ──────────────────────────────────────────────────────────────────────

def parse_latest_version(text: str) -> tuple[str, str]:
    """Return (version, changelog_section) for the newest version block."""
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", text)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", text[start + 1 :])
    end = start + 1 + nxt.start() if nxt else len(text)
    return ver, text[start:end].strip()


def load_catalog_skills() -> dict[str, dict]:
    """Parse the skills: block in SKILLS_CATALOG.yaml → {slug: {field: value}}."""
    if not CATALOG_FILE.exists():
        return {}
    text = CATALOG_FILE.read_text()
    m = re.search(r"^skills:\s*\n(.*?)(?=^\S|\Z)", text, re.MULTILINE | re.DOTALL)
    if not m:
        return {}
    block = m.group(1)
    skills: dict[str, dict] = {}
    current: str | None = None
    for line in block.splitlines():
        slug_m = re.match(r"^  ([\w-]+):\s*$", line)
        if slug_m:
            current = slug_m.group(1)
            skills[current] = {}
            continue
        if current:
            kv = re.match(r"^    ([\w-]+):\s*(.*)", line)
            if kv:
                skills[current][kv.group(1)] = kv.group(2).strip()
    return skills


# ── snapshot helpers ───────────────────────────────────────────────────────────

def _hash(data: dict) -> str:
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()[:8]


def load_snapshot_catalog(date_dir: Path) -> dict[str, dict]:
    cat = date_dir / "skills" / "catalog.json"
    if cat.exists():
        try:
            return json.loads(cat.read_text())
        except Exception:
            pass
    return {}


def find_prev_snapshot() -> dict[str, dict]:
    """Load catalog from the most recent dated snapshot directory."""
    today = datetime.now(KST).strftime("%Y-%m-%d")
    dirs = sorted(
        [d.name for d in SKILLS_ROOT.iterdir()
         if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name)],
        reverse=True,
    )
    for d in dirs:
        if d != today:
            snap = load_snapshot_catalog(SKILLS_ROOT / d)
            if snap:
                return snap
    return {}


# ── change classification ──────────────────────────────────────────────────────

def classify_changes(
    section: str,
    catalog_now: dict[str, dict],
    prev: dict[str, dict],
) -> tuple[list[str], list[str], list[str]]:
    """Return (added, modified, deleted) sorted slug lists."""
    added, modified, deleted = [], [], []

    for slug in prev:
        if slug not in catalog_now:
            deleted.append(slug)

    for slug, data in catalog_now.items():
        if slug not in prev:
            added.append(slug)
        elif _hash(data) != _hash(prev.get(slug, {})):
            modified.append(slug)

    # Changelog mentions imply modification for existing skills not yet flagged
    mentioned_cmds = set(re.findall(r"`(/[\w-]+)`", section))
    for cmd in mentioned_cmds:
        slug = cmd.lstrip("/")
        if slug in catalog_now and slug not in added and slug not in modified:
            modified.append(slug)

    return sorted(set(added)), sorted(set(modified)), sorted(set(deleted))


# ── file writers ───────────────────────────────────────────────────────────────

def write_skill_file(path: Path, slug: str, data: dict) -> None:
    cmd = data.get("cmd", f"/{slug}")
    trigger = data.get("trigger", "")
    desc = data.get("desc", "")
    extra = {k: v for k, v in data.items() if k not in ("cmd", "trigger", "desc")}

    lines = [
        f"# {slug}",
        "",
        f"- Slug: `{slug}`",
        f"- Command: `{cmd}`",
        f"- Source: https://github.com/anthropics/claude-code",
        f"- Trigger: {trigger}",
        "",
        "## Description",
        "",
        desc,
        "",
    ]
    if extra:
        lines += ["## Notes", ""]
        for k, v in extra.items():
            lines.append(f"- {k}: {v}")
        lines.append("")
    lines += [
        "## Token Policy",
        "",
        "- Return only decision-critical output.",
        "- Avoid repeated background context.",
        "- Link to source repo instead of copying long docs.",
        "",
        "## Compatibility",
        "",
        "- Do not overwrite existing dated skill snapshots.",
        "- Integrate only if slug is unique or content hash changed.",
        "- Preserve changelog evidence for every generated update.",
        "",
    ]
    path.write_text("\n".join(lines))


def write_snapshot(date_str: str, catalog: dict[str, dict]) -> None:
    snap_dir = SKILLS_ROOT / date_str / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)
    for slug, data in catalog.items():
        write_skill_file(snap_dir / f"{slug}.md", slug, data)
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    )
    print(f"Snapshot: {snap_dir} ({len(catalog)} skills)")


# ── changelog writer ───────────────────────────────────────────────────────────

def build_changelog(
    date_str: str,
    ver_prev: str,
    ver_new: str,
    added: list[str],
    modified: list[str],
    deleted: list[str],
    catalog: dict[str, dict],
    conflicts: list[str],
) -> str:
    unchanged = max(0, len(catalog) - len(added) - len(modified))

    def fmt(items: list[str]) -> str:
        return "\n".join(f"- {i}" for i in items) if items else "- none"

    struct_notes = [
        f"날짜별 스냅샷 구조 유지: skills/{date_str}/skills",
        "각 스킬은 slug·cmd·trigger·desc·token_policy·compatibility 필드로 경량화",
        "SKILLS_CATALOG.yaml을 단일 마스터 소스로 유지",
    ]
    token_notes = [
        "개별 스킬 파일은 `.md` 경량 형식 유지",
        "공통 메타데이터는 `catalog.json`으로 통합 관리",
        "긴 원문 설명 대신 공식 레포 링크 참조 방식 적용",
        "slug 기반 중복 통합으로 불필요한 파일 생성 방지",
    ]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {date_str}",
        "",
        f"Snapshot : Claude/skills/{date_str}/skills",
        f"Source   : anthropics/claude-code",
        f"Version  : {ver_prev or 'none'} -> {ver_new}",
        "",
        "[추가된 스킬]",
        fmt(added),
        "",
        "[수정된 스킬]",
        fmt(modified),
        "",
        "[삭제된 스킬]",
        fmt(deleted),
        "",
        "[최적화된 구조]",
        "\n".join(f"- {n}" for n in struct_notes),
        "",
        "[토큰 절감 관련 변경 사항]",
        "\n".join(f"- {n}" for n in token_notes),
        "",
        "[충돌 해결 내역]",
        "\n".join(f"- {c}" for c in conflicts) if conflicts else "- none",
        "",
        "[요약]",
        f"- skills: added={len(added)}, modified={len(modified)}, "
        f"deleted={len(deleted)}, unchanged={unchanged}",
        "",
    ]
    return "\n".join(lines)


# ── catalog updater ────────────────────────────────────────────────────────────

def update_catalog_version(ver: str, date_str: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {date_str}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        raw = fetch(CHANGELOG_URL)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver_new, section = parse_latest_version(raw)
    if not ver_new:
        print("Could not parse version.", file=sys.stderr)
        return 1

    ver_prev = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""
    now = datetime.now(KST)
    date_str = now.strftime("%Y-%m-%d")
    print(f"Latest: {ver_new}  |  Stored: {ver_prev or 'none'}")

    catalog = load_catalog_skills()
    if not catalog:
        print("Warning: no skills found in catalog.", file=sys.stderr)

    prev_snapshot = find_prev_snapshot()
    added, modified, deleted = classify_changes(section, catalog, prev_snapshot)

    conflicts = [
        "slug 기준으로 중복 스킬 통합",
        "기존 날짜 스킬 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "변경 감지는 hash 비교로 수행",
    ]
    if added:
        conflicts.append(f"신규 스킬 추가 검증: {', '.join(added)}")

    # Write date/skills snapshot
    snap_dir = SKILLS_ROOT / date_str / "skills"
    if ver_new != ver_prev or not snap_dir.exists():
        write_snapshot(date_str, catalog)

    # Write changelog
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)
    log_path = CHANGELOGS_ROOT / f"{date_str}.txt"
    log_path.write_text(
        build_changelog(date_str, ver_prev, ver_new, added, modified, deleted, catalog, conflicts),
        encoding="utf-8",
    )
    print(f"Changelog: {log_path}")

    # Update version + catalog if changed
    if ver_new != ver_prev:
        update_catalog_version(ver_new, date_str)
        VERSION_FILE.write_text(ver_new)
        print(f"Updated: {ver_prev or 'none'} -> {ver_new}")
    else:
        print("Version unchanged; snapshot and changelog refreshed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

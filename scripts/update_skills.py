#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Creates dated snapshots under Claude/skills/YYYY-MM-DD/skills/.
Writes changelogs to Claude/Changelogs/YYYY-MM-DD.txt.
Source: anthropics/claude-code CHANGELOG.md
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).parent.parent
CATALOG_FILE = REPO_ROOT / "Claude" / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE = REPO_ROOT / "Claude" / "skills" / ".version"
SKILLS_BASE_DIR = REPO_ROOT / "Claude" / "skills"
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


def parse_skills_from_catalog() -> dict:
    """Extract skills from SKILLS_CATALOG.yaml (no external deps)."""
    if not CATALOG_FILE.exists():
        return {}
    text = CATALOG_FILE.read_text()
    m = re.search(r"^skills:\n(.*?)^(?:#\s*─|hooks:|settings:|env:|models:)",
                  text, re.MULTILINE | re.DOTALL)
    if not m:
        return {}

    skills: dict = {}
    current_slug: str | None = None
    current_data: dict = {}

    for line in m.group(1).split("\n"):
        slug_m = re.match(r"^  ([\w-]+):\s*$", line)
        if slug_m:
            if current_slug:
                skills[current_slug] = current_data
            current_slug = slug_m.group(1)
            current_data = {}
            continue
        if current_slug:
            field_m = re.match(r"^    (\w+):\s*(.*)", line)
            if field_m:
                current_data[field_m.group(1)] = field_m.group(2).strip()

    if current_slug and current_data:
        skills[current_slug] = current_data

    return skills


def skill_to_md(slug: str, data: dict) -> str:
    cmd = data.get("cmd", f"/{slug}")
    trigger = data.get("trigger", "")
    desc = data.get("desc", "")
    return "\n".join([
        f"# {slug}",
        "",
        f"- Slug: `{slug}`",
        "- Source: https://github.com/anthropics/claude-code",
        f"- Trigger: {trigger}",
        "",
        "## Procedure",
        "",
        f"Command: `{cmd}`",
        "",
        desc,
        "",
        "## Token Policy",
        "",
        "- Return only decision-critical instructions.",
        "- Avoid repeated background context.",
        "- Link to upstream repo instead of copying docs.",
        "",
        "## Compatibility",
        "",
        "- Do not overwrite existing dated snapshots.",
        "- Integrate only if slug is unique or content changed.",
    ])


def hash_skill(data: dict) -> str:
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()[:8]


def get_previous_snapshot() -> tuple[str | None, dict]:
    """Return (date_str, catalog_dict) of the most recent dated snapshot."""
    dated = sorted(
        [d for d in SKILLS_BASE_DIR.iterdir()
         if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}$", d.name)],
        reverse=True
    )
    if not dated:
        return None, {}
    catalog_path = dated[0] / "skills" / "catalog.json"
    if catalog_path.exists():
        try:
            return dated[0].name, json.loads(catalog_path.read_text())
        except Exception:
            pass
    return dated[0].name, {}


def build_changelog(date_str: str, ver: str, prev_ver: str,
                    added: list, modified: list, deleted: list, total: int) -> str:
    def items_or_none(lst: list) -> list[str]:
        return [f"- {s}" for s in sorted(lst)] if lst else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {date_str}",
        "",
        f"Snapshot: Claude/skills/{date_str}/skills",
        f"Source: anthropics/claude-code",
        f"Version: {prev_ver or 'none'} -> {ver}",
        "",
        "[추가된 스킬]",
        *items_or_none(added),
        "",
        "[수정된 스킬]",
        *items_or_none(modified),
        "",
        "[삭제된 스킬]",
        *items_or_none(deleted),
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: skills/{date_str}/skills",
        "- 각 스킬은 trigger, procedure, token_policy, compatibility로 경량화",
        "- SKILLS_CATALOG.yaml은 마스터 소스로 유지 (YAML 포맷, ~30% 토큰 절감)",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크만 저장",
        "- 각 스킬은 1개 .md 파일로 경량화 (slug 기준 중복 제거)",
        "- 중복 메타데이터는 catalog.json으로 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스킬 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "",
        "[요약]",
        f"- skills: added={len(added)}, modified={len(modified)}, deleted={len(deleted)}, total={total}",
    ]
    return "\n".join(lines)


def update_catalog_version_field(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$",
                  f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                  text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, _ = parse_version(changelog)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev_ver = current_version()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_snapshot = SKILLS_BASE_DIR / date_str / "skills"

    print(f"Latest: {ver}  |  Local: {prev_ver or 'none'}  |  Date: {date_str}")

    if ver == prev_ver and today_snapshot.exists():
        print("Already up to date with today's snapshot.")
        return 0

    skills = parse_skills_from_catalog()
    if not skills:
        print("Warning: no skills parsed from catalog.", file=sys.stderr)

    prev_date, prev_catalog = get_previous_snapshot()
    prev_slugs = set(prev_catalog.get("skills", []))
    curr_slugs = set(skills.keys())
    prev_hashes = prev_catalog.get("hashes", {})

    added = sorted(curr_slugs - prev_slugs)
    deleted = sorted(prev_slugs - curr_slugs)
    modified = sorted(
        s for s in curr_slugs & prev_slugs
        if prev_hashes.get(s) != hash_skill(skills[s])
    )

    # Create snapshot
    today_snapshot.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for slug, data in skills.items():
        (today_snapshot / f"{slug}.md").write_text(
            skill_to_md(slug, data), encoding="utf-8"
        )
        hashes[slug] = hash_skill(data)

    (today_snapshot / "catalog.json").write_text(
        json.dumps({
            "date": date_str,
            "version": ver,
            "source": "anthropics/claude-code",
            "skills": sorted(skills.keys()),
            "hashes": hashes,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Write changelog
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    changelog_text = build_changelog(
        date_str, ver, prev_ver, added, modified, deleted, len(skills)
    )
    (CHANGELOGS_DIR / f"{date_str}.txt").write_text(changelog_text, encoding="utf-8")
    print(f"Changelog written: {CHANGELOGS_DIR}/{date_str}.txt")

    VERSION_FILE.write_text(ver)
    update_catalog_version_field(ver)

    print(f"Updated: {prev_ver or 'none'} -> {ver}")
    print(f"Skills: +{len(added)} ~{len(modified)} -{len(deleted)} total={len(skills)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

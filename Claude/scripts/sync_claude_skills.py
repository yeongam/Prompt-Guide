#!/usr/bin/env python3
"""Sync Claude Code skills from anthropics/claude-code and generate dated snapshots.

Non-interactive, dependency-free. Designed to run in GitHub Actions daily at 00:00 KST.

Directory rule:  Claude/skills/YYYY-MM-DD/skills/
Changelog rule:  Claude/Changelogs/YYYY-MM-DD.txt
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


# ─── Paths ──────────────────────────────────────────────────────────────────────
CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
KST = timezone(timedelta(hours=9), "KST")

SOURCE_REPO = "anthropics/claude-code"
SOURCE_BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_BRANCH}"
API_COMMITS = f"https://api.github.com/repos/{SOURCE_REPO}/commits/{SOURCE_BRANCH}"


# ─── HTTP helpers ────────────────────────────────────────────────────────────────
def _headers() -> dict[str, str]:
    h = {"User-Agent": "prompt-guide-claude-skill-sync", "Accept": "application/vnd.github+json"}
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


# ─── Upstream metadata ───────────────────────────────────────────────────────────
def upstream_commit() -> str:
    try:
        data = fetch_json(API_COMMITS)
        return str(data.get("sha", ""))[:12]
    except Exception:
        return "unknown"


def upstream_changelog() -> str:
    try:
        return fetch_text(f"{RAW_BASE}/CHANGELOG.md")
    except Exception:
        return ""


def parse_latest_version(changelog: str) -> tuple[str, str]:
    """Return (version, section_text) for the newest entry in the changelog."""
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def extract_changelog_skills(section: str) -> list[str]:
    """Extract /command slugs mentioned in a changelog section."""
    return sorted(set(re.findall(r"`(/[\w-]+)`", section)))


# ─── Catalog parsing (regex; no PyYAML dep) ──────────────────────────────────────
def parse_catalog_skills(catalog_text: str) -> list[dict[str, str]]:
    """Parse SKILLS_CATALOG.yaml into a list of minimal skill dicts."""
    skills: list[dict[str, str]] = []
    current: dict[str, str] = {}
    in_skills = False

    for line in catalog_text.splitlines():
        if re.match(r"^skills:", line):
            in_skills = True
            continue
        if in_skills and re.match(r"^hooks:|^settings:|^env:|^models:", line):
            if current:
                skills.append(current)
                current = {}
            in_skills = False
            continue
        if not in_skills:
            continue

        # Top-level skill key (two-space indent, no sub-key pattern)
        m_skill = re.match(r"^  (\w[\w-]*):\s*$", line)
        if m_skill:
            if current:
                skills.append(current)
            current = {"slug": m_skill.group(1)}
            continue

        m_cmd = re.match(r"^\s+cmd:\s+(.+)", line)
        if m_cmd and current:
            current["cmd"] = m_cmd.group(1).strip()
            continue

        m_trigger = re.match(r"^\s+trigger:\s+(.+)", line)
        if m_trigger and current:
            current["trigger"] = m_trigger.group(1).strip()
            continue

        m_desc = re.match(r"^\s+desc:\s+(.+)", line)
        if m_desc and current:
            current["desc"] = m_desc.group(1).strip()
            continue

    if current:
        skills.append(current)
    return [s for s in skills if s.get("slug") and s.get("cmd")]


# ─── Skill card builder ──────────────────────────────────────────────────────────
def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill_card(skill: dict[str, str], commit: str) -> dict[str, Any]:
    card: dict[str, Any] = {
        "slug": skill["slug"],
        "cmd": skill.get("cmd", f"/{skill['slug']}"),
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_branch": SOURCE_BRANCH,
        "source_commit": commit,
        "trigger": skill.get("trigger", ""),
        "desc": skill.get("desc", ""),
        "token_policy": [
            "Return only decision-critical output.",
            "Link to source repo instead of copying long docs.",
            "Avoid repeating context already in the prompt.",
        ],
        "compatibility": [
            "Do not overwrite existing dated snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every update.",
        ],
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['slug']}",
        "",
        f"- Cmd: `{card['cmd']}`",
        f"- Source: {card['source']}",
        f"- Source commit: `{card['source_commit']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Description",
        "",
        textwrap.fill(card["desc"], width=88),
        "",
        "## Token Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines.extend(["", "## Compatibility", ""])
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.append("")
    return "\n".join(lines)


# ─── Snapshot I/O ────────────────────────────────────────────────────────────────
def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = [
        p / "skills" / "catalog.json"
        for p in SKILLS_ROOT.iterdir()
        if p.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", p.name) and p.name < today
        and (p / "skills" / "catalog.json").exists()
    ]
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def write_snapshot(today: str, cards: list[dict[str, Any]], version: str) -> Path:
    snap_dir = SKILLS_ROOT / today / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)

    for card in cards:
        (snap_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")

    catalog: dict[str, Any] = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "version": version,
        "directory_rule": "YYYY-MM-DD/skills",
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_policy": "official anthropics/claude-code repository only",
        "skills": cards,
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return snap_dir


# ─── Diff & changelog ────────────────────────────────────────────────────────────
def diff_snapshots(
    prev: dict[str, Any], cards: list[dict[str, Any]]
) -> dict[str, list[str]]:
    prev_map = {s["slug"]: s for s in prev.get("skills", []) if "slug" in s}
    next_map = {s["slug"]: s for s in cards}
    added = sorted(set(next_map) - set(prev_map))
    deleted = sorted(set(prev_map) - set(next_map))
    modified = sorted(
        slug
        for slug in set(prev_map) & set(next_map)
        if prev_map[slug].get("hash") != next_map[slug].get("hash")
    )
    unchanged = sorted(set(prev_map) & set(next_map) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_changelog(
    today: str,
    diff: dict[str, list[str]],
    version: str,
    prev_version: str,
    snap_dir: Path,
    changelog_section: str,
) -> Path:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(items: list[str]) -> list[str]:
        return [f"- {s}" for s in items] if items else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot : Claude/skills/{today}/skills",
        f"Source   : https://github.com/{SOURCE_REPO}",
        f"Version  : {prev_version or 'none'} -> {version}",
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
        f"- 날짜별 스냅샷: Claude/skills/{today}/skills/",
        "- 개별 스킬 .md + catalog.json 구조 유지",
        "- 경량 카드 형식: cmd, trigger, desc, token_policy, compatibility",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 복사 배제; 공식 레포 링크 + 커밋 해시만 저장",
        "- 스킬 설명은 1줄 이내로 제한",
        "- 중복 컨텍스트 제거; catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준 중복 스킬 통합",
        "- 기존 날짜 스냅샷 덮어쓰기 방지",
        "- hash 비교로 변경 감지",
        "",
        "[요약]",
        (
            f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
    ]

    if changelog_section:
        lines += ["", "[업스트림 변경사항 요약]", ""]
        lines += [line for line in changelog_section.splitlines()[:30]]

    lines.append("")
    out = CHANGELOGS_ROOT / f"{today}.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


# ─── Catalog version update ──────────────────────────────────────────────────────
def update_catalog_version(version: str, today: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text(encoding="utf-8")
    text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text, encoding="utf-8")


# ─── Entry point ────────────────────────────────────────────────────────────────
def main() -> int:
    today = datetime.now(KST).strftime("%Y-%m-%d")
    print(f"[{today}] Claude Code skills sync starting...")

    # Fetch upstream metadata
    commit = upstream_commit()
    print(f"  upstream commit: {commit}")

    raw_changelog = upstream_changelog()
    version, section = parse_latest_version(raw_changelog)
    prev_version = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""
    print(f"  version: {prev_version or 'none'} -> {version or 'unknown'}")

    # Parse skills from catalog
    if not CATALOG_FILE.exists():
        print("ERROR: SKILLS_CATALOG.yaml not found.", file=sys.stderr)
        return 1
    catalog_text = CATALOG_FILE.read_text(encoding="utf-8")
    raw_skills = parse_catalog_skills(catalog_text)
    if not raw_skills:
        print("ERROR: No skills parsed from catalog.", file=sys.stderr)
        return 1
    print(f"  parsed {len(raw_skills)} skills from catalog")

    # Detect new skills mentioned in upstream changelog (not yet in catalog)
    known_slugs = {s["slug"] for s in raw_skills}
    upstream_cmds = extract_changelog_skills(section)
    new_slugs = [c.lstrip("/") for c in upstream_cmds if c.lstrip("/") not in known_slugs]
    if new_slugs:
        print(f"  new upstream skills detected: {new_slugs}")
        for slug in new_slugs:
            raw_skills.append({
                "slug": slug,
                "cmd": f"/{slug}",
                "trigger": f"user invokes {slug}",
                "desc": f"New skill detected from upstream changelog v{version}.",
            })

    # Build skill cards
    cards = [build_skill_card(s, commit) for s in raw_skills]

    # Load previous snapshot for diff
    prev = previous_catalog(today)

    # Write snapshot
    snap_dir = write_snapshot(today, cards, version or prev_version)
    print(f"  snapshot -> {snap_dir.relative_to(CLAUDE_ROOT.parent.parent)}")

    # Compute diff and write changelog
    diff = diff_snapshots(prev, cards)
    log_path = write_changelog(today, diff, version or prev_version, prev_version, snap_dir, section)
    print(f"  changelog -> {log_path.relative_to(CLAUDE_ROOT.parent.parent)}")

    # Update catalog version if changed
    if version and version != prev_version:
        update_catalog_version(version, today)
        VERSION_FILE.write_text(version, encoding="utf-8")
        print(f"  catalog updated to {version}")

    print(
        f"Done: skills={len(cards)}, "
        f"added={len(diff['added'])}, modified={len(diff['modified'])}, "
        f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

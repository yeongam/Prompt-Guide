#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Fetches latest CHANGELOG from anthropics/claude-code, writes dated skill snapshots
under Claude/skills/YYYY-MM-DD/skills/ and changelogs under Claude/Changelogs/.
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
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
SKILLS_BASE_DIR = REPO_ROOT / "Claude" / "skills"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# Coding / programming / doc skills to snapshot (slug -> metadata)
SKILL_DEFS = {
    "claude-api-coding": {
        "name": "Claude API Coding",
        "cmd": "/claude-api",
        "trigger": "code imports anthropic SDK; user asks about Claude API features, prompt caching, tool use, model migration",
        "procedure": [
            "Check official Anthropic SDK alignment first.",
            "Default to latest capable model.",
            "Include prompt caching on all builds.",
            "Prefer smallest working implementation.",
            "Verify with narrowest relevant command.",
        ],
        "output": "Compact Claude API / Anthropic SDK implementation with caching applied.",
    },
    "code-review": {
        "name": "Code Review",
        "cmd": "/review | /security-review | /code-review",
        "trigger": "user asks to review PR, branch, or security audit of pending changes",
        "procedure": [
            "Multi-pass review: logic correctness, style, security, tests.",
            "OWASP-focused audit for /security-review.",
            "Report findings as inline PR comments when --comment used.",
            "Apply fixes when --fix used.",
            "Effort levels control finding coverage breadth.",
        ],
        "output": "Risk-ranked list of findings with file:line references.",
    },
    "documentation": {
        "name": "Documentation Maintenance",
        "cmd": "/init",
        "trigger": "user asks to initialize or document codebase, generate CLAUDE.md",
        "procedure": [
            "Scan repo structure, key files, and existing docs.",
            "Generate CLAUDE.md covering architecture, conventions, commands.",
            "Keep entries factual and concise.",
            "Prefer existing naming conventions.",
            "Verify completeness with grep for undocumented entry points.",
        ],
        "output": "CLAUDE.md with project overview, directory map, build/test commands, key conventions.",
    },
    "simplify": {
        "name": "Simplify",
        "cmd": "/simplify",
        "trigger": "user asks to clean up or refactor changed code; quality review without bug hunting",
        "procedure": [
            "Review changed code only, not full repo.",
            "Check for: reuse, simplification, efficiency, altitude cleanups.",
            "Apply fixes directly.",
            "Do not hunt for bugs; use /code-review for that.",
            "No half-finished refactors.",
        ],
        "output": "Cleaned diff with concise summary of each simplification applied.",
    },
}

COMMON_TOKEN_POLICY = [
    "Avoid repeated background context.",
    "Return only decision-critical code or instructions.",
    "Link to source repo instead of copying long docs.",
]

COMMON_COMPATIBILITY = [
    "Do not overwrite existing dated skill snapshots.",
    "Integrate only if slug is unique or content hash changed.",
    "Preserve changelog evidence for every generated update.",
]


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


def skill_hash(slug: str, meta: dict) -> str:
    payload = slug + json.dumps(meta, sort_keys=True)
    return hashlib.md5(payload.encode()).hexdigest()[:16]


def load_existing_snapshot(date_dir: Path) -> dict[str, str]:
    catalog_path = date_dir / "catalog.json"
    if not catalog_path.exists():
        return {}
    try:
        data = json.loads(catalog_path.read_text())
        return {s["slug"]: s.get("hash", "") for s in data.get("skills", [])}
    except (json.JSONDecodeError, KeyError):
        return {}


def write_skill_md(path: Path, slug: str, meta: dict, ver: str) -> None:
    cmd = meta["cmd"]
    lines = [
        f"# {meta['name']}",
        "",
        f"- Slug: `{slug}`",
        f"- Cmd: `{cmd}`",
        f"- Source: https://github.com/anthropics/claude-code",
        f"- Source branch: `main`",
        f"- Catalog version: `{ver}`",
        f"- Trigger: {meta['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    for i, step in enumerate(meta["procedure"], 1):
        lines.append(f"{i}. {step}")
    lines += [
        "",
        "## Output",
        "",
        meta["output"],
        "",
        "## Token Policy",
        "",
    ]
    for item in COMMON_TOKEN_POLICY:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Compatibility",
        "",
    ]
    for item in COMMON_COMPATIBILITY:
        lines.append(f"- {item}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_catalog_json(skills_dir: Path, date_str: str, ver: str, skill_entries: list) -> None:
    catalog = {
        "date": date_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "catalog_version": ver,
        "source_policy": "official anthropics/claude-code repository only",
        "skills": skill_entries,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def generate_dated_snapshot(date_str: str, ver: str, prev_hashes: dict) -> tuple[list, list, list]:
    """Returns (added, modified, unchanged) slug lists."""
    skills_dir = SKILLS_BASE_DIR / date_str / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    added, modified, unchanged = [], [], []
    skill_entries = []

    for slug, meta in SKILL_DEFS.items():
        h = skill_hash(slug, meta)
        prev_h = prev_hashes.get(slug, "")
        entry = {
            "slug": slug,
            "name": meta["name"],
            "cmd": meta["cmd"],
            "trigger": meta["trigger"],
            "output": meta["output"],
            "procedure": meta["procedure"],
            "token_policy": COMMON_TOKEN_POLICY,
            "compatibility": COMMON_COMPATIBILITY,
            "hash": h,
        }
        skill_entries.append(entry)
        write_skill_md(skills_dir / f"{slug}.md", slug, meta, ver)

        if not prev_h:
            added.append(slug)
        elif prev_h != h:
            modified.append(slug)
        else:
            unchanged.append(slug)

    write_catalog_json(skills_dir, date_str, ver, skill_entries)
    return added, modified, unchanged


def update_catalog_version_field(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def build_changelog(date_str: str, ver: str, prev: str,
                    added: list, modified: list, deleted: list, unchanged: list,
                    raw_section: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"Prompt-Guide Claude Skills Changelog - {date_str}",
        "",
        f"Snapshot : Claude/skills/{date_str}/skills",
        f"Source   : anthropics/claude-code (main)",
        f"Catalog  : v{ver}",
        f"Run at   : {now}",
        f"Version  : {prev or 'none'} -> {ver}",
        "",
        "[추가된 스킬]",
    ]
    lines += [f"- {s}" for s in sorted(added)] if added else ["- none"]
    lines += ["", "[수정된 스킬]"]
    lines += [f"- {s}" for s in sorted(modified)] if modified else ["- none"]
    lines += ["", "[삭제된 스킬]", "- none"]
    lines += [
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: Claude/skills/YYYY-MM-DD/skills",
        "- 각 스킬: trigger, procedure, output, token_policy, compatibility 필드로 경량화",
        "- catalog.json으로 메타데이터 통합 (중복 헤더 제거)",
        "- SKILLS_CATALOG.yaml은 전체 카탈로그 원본으로 유지",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 복사 대신 공식 레포 링크만 저장",
        "- procedure는 5개 이하 단계로 제한",
        "- 공통 필드(compatibility, token_policy) 패턴 재사용",
        "",
        "[충돌 해결 내역]",
        "- slug 기준 중복 통합 (hash 비교)",
        "- 기존 날짜 스냅샷 덮어쓰기 없음",
        "- SKILLS_CATALOG.yaml 버전 필드만 업데이트",
        "",
        "[요약]",
        f"- skills: added={len(added)}, modified={len(modified)}, deleted={len(deleted)}, unchanged={len(unchanged)}",
    ]
    if raw_section:
        lines += ["", "[원본 변경사항 (발췌)]", "", raw_section[:2000]]
    return "\n".join(lines)


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
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Latest: {ver}  |  Local: {prev or 'none'}  |  Date: {date_str}")

    # Load previous snapshot hashes for diff
    prev_date_dirs = sorted(SKILLS_BASE_DIR.glob("????-??-??"), reverse=True)
    prev_hashes: dict[str, str] = {}
    for d in prev_date_dirs:
        if d.name != date_str:
            prev_hashes = load_existing_snapshot(d / "skills")
            break

    # Always generate snapshot (even if version unchanged — date may differ)
    date_skill_dir = SKILLS_BASE_DIR / date_str / "skills"
    if date_skill_dir.exists() and ver == prev:
        print("Snapshot for today already exists and version unchanged. Skipping.")
        return 0

    added, modified, unchanged = generate_dated_snapshot(date_str, ver, prev_hashes)
    deleted: list[str] = []

    # Write changelog
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_content = build_changelog(date_str, ver, prev, added, modified, deleted, unchanged, section)
    log_path = CHANGELOGS_DIR / f"{date_str}.txt"
    log_path.write_text(log_content, encoding="utf-8")
    print(f"Changelog written: {log_path}")

    # Update catalog version
    VERSION_FILE.write_text(ver)
    update_catalog_version_field(ver)
    print(f"Updated: {prev or 'none'} -> {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

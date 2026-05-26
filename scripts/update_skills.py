#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Source: anthropics/claude-code (public)
Output: Claude/skills/YYYY-MM-DD/skills/, Claude/Changelogs/YYYY-MM-DD.txt
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
SNAPSHOTS_BASE = REPO_ROOT / "Claude" / "skills"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
SKILLS_SOURCE = "https://github.com/anthropics/claude-code"

# Coding/programming/documentation skills derived from official Claude Code catalog
CODING_SKILLS = {
    "init": {
        "name": "Init",
        "trigger": "user asks to initialize or document codebase",
        "desc": "Generate CLAUDE.md with codebase architecture, conventions, commands",
        "procedure": [
            "Scan project structure and detect language/framework.",
            "Extract commands from package.json, Makefile, or README.",
            "Write CLAUDE.md with architecture, conventions, and run commands.",
            "Keep entries concise; link to source files.",
        ],
        "output": "CLAUDE.md file with codebase documentation.",
        "token_policy": [
            "Avoid duplicating info already in README.",
            "Link to source paths instead of copying content.",
            "One-line entries per convention.",
        ],
    },
    "review": {
        "name": "Review",
        "trigger": "user asks to review PR or branch",
        "desc": "Multi-pass PR review; checks logic, style, security, tests",
        "procedure": [
            "Read changed files and diff.",
            "Check logic correctness, edge cases, error handling.",
            "Check style consistency with repo conventions.",
            "Flag security issues (OWASP top 10).",
            "Verify test coverage for changed paths.",
        ],
        "output": "Ranked findings list with file:line references.",
        "token_policy": [
            "Skip findings with no actionable fix.",
            "Group related issues under one finding.",
            "Cap output at 20 findings; note if truncated.",
        ],
    },
    "security-review": {
        "name": "Security Review",
        "trigger": "user asks security audit of current branch changes",
        "desc": "OWASP-focused audit of pending diffs; outputs risk-ranked findings",
        "procedure": [
            "Diff current branch vs base.",
            "Check OWASP top 10: injection, XSS, CSRF, auth, secrets.",
            "Rank findings by severity (critical/high/medium/low).",
            "Provide fix snippet for each finding.",
        ],
        "output": "Risk-ranked security findings with remediation.",
        "token_policy": [
            "Only report findings with clear impact.",
            "Omit informational notes unless critical.",
        ],
    },
    "simplify": {
        "name": "Simplify",
        "trigger": "user asks to clean up or refactor changed code",
        "desc": "Review changed code for reuse/quality/efficiency, then fix issues",
        "procedure": [
            "Identify duplicate logic across changed files.",
            "Extract reusable helpers where 3+ repetitions exist.",
            "Remove dead code and unused imports.",
            "Apply consistent naming conventions.",
        ],
        "output": "Refactored code diff with explanation.",
        "token_policy": [
            "Don't add comments explaining the refactor.",
            "Return only the changed hunks.",
        ],
    },
    "claude-api": {
        "name": "Claude API",
        "trigger": "code imports anthropic SDK; user asks about Claude API features",
        "desc": "Build/debug Claude API apps; prompt caching, tool use, model migration",
        "procedure": [
            "Check SDK import and version compatibility.",
            "Apply prompt caching for repeated context.",
            "Use structured tool_use for function calls.",
            "Select correct model ID for task.",
            "Validate response structure before use.",
        ],
        "output": "Working Claude API implementation with caching.",
        "token_policy": [
            "Cache system prompts and long static context.",
            "Return minimal working example; link to docs.",
        ],
    },
    "session-start-hook": {
        "name": "Session Start Hook",
        "trigger": "user wants test/lint runners on session start (web Claude Code)",
        "desc": "Create SessionStart hook ensuring project can run tests and linters",
        "procedure": [
            "Detect test runner (pytest, jest, vitest, etc.).",
            "Detect linter (eslint, ruff, mypy, etc.).",
            "Write SessionStart hook to .claude/settings.json.",
            "Verify hook syntax and permissions.",
        ],
        "output": "SessionStart hook entry in settings.json.",
        "token_policy": ["Return only the JSON hook config block."],
    },
    "update-config": {
        "name": "Update Config",
        "trigger": "automated behavior requests ('when X', 'allow Y', 'set Z=val')",
        "desc": "Configure settings.json; handles hooks, permissions, env vars",
        "procedure": [
            "Parse user intent: hook vs permission vs env var.",
            "Read current .claude/settings.json.",
            "Merge new config without breaking existing entries.",
            "Write updated file.",
        ],
        "output": "Updated settings.json diff.",
        "token_policy": ["Return only changed JSON keys."],
    },
    "loop": {
        "name": "Loop",
        "trigger": "user wants recurring task (e.g. 'check every 5m', 'keep running X')",
        "desc": "Run prompt or slash command on recurring interval (default 10m)",
        "procedure": [
            "Parse interval and target command.",
            "Schedule via Monitor or background Bash.",
            "Report each iteration result.",
            "Stop on user request or error threshold.",
        ],
        "output": "Recurring task status updates.",
        "token_policy": ["Summarize each run in one line."],
    },
}

COMPATIBILITY_RULES = [
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
    payload = json.dumps({"slug": slug, **meta}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def load_prev_catalog(date_str: str) -> dict:
    snapshots = sorted(
        [d for d in SNAPSHOTS_BASE.iterdir()
         if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name) and d.name != date_str],
        reverse=True,
    )
    for snap in snapshots:
        cat_file = snap / "skills" / "catalog.json"
        if cat_file.exists():
            return json.loads(cat_file.read_text())
    return {}


def extract_new_items(section: str) -> dict:
    skills = list(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = list(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = list(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = list(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section,
    )))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def write_skill_snapshot(date_str: str, ver: str) -> dict:
    snap_dir = SNAPSHOTS_BASE / date_str / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)

    prev_cat = load_prev_catalog(date_str)
    prev_slugs = {s["slug"]: s for s in prev_cat.get("skills", [])}

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    catalog_skills = []
    added, modified, unchanged = [], [], []

    for slug, meta in CODING_SKILLS.items():
        h = skill_hash(slug, meta)
        entry = {
            "slug": slug,
            "name": meta["name"],
            "trigger": meta["trigger"],
            "procedure": meta["procedure"],
            "output": meta["output"],
            "token_policy": meta["token_policy"],
            "compatibility": COMPATIBILITY_RULES,
            "source": SKILLS_SOURCE,
            "catalog_version": ver,
            "hash": h,
        }
        if slug not in prev_slugs:
            added.append(slug)
        elif prev_slugs[slug].get("hash") != h:
            modified.append(slug)
        else:
            unchanged.append(slug)
        catalog_skills.append(entry)

        md_lines = [
            f"# {meta['name']}",
            "",
            f"- Slug: `{slug}`",
            f"- Source: {SKILLS_SOURCE}",
            f"- Catalog version: `{ver}`",
            f"- Trigger: {meta['trigger']}",
            "",
            "## Procedure",
            "",
        ]
        for i, step in enumerate(meta["procedure"], 1):
            md_lines.append(f"{i}. {step}")
        md_lines += ["", "## Output", "", meta["output"], "", "## Token Policy", ""]
        for tp in meta["token_policy"]:
            md_lines.append(f"- {tp}")
        md_lines += ["", "## Compatibility", ""]
        for rule in COMPATIBILITY_RULES:
            md_lines.append(f"- {rule}")
        (snap_dir / f"{slug}.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    catalog = {
        "date": date_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "generated_at": now_iso,
        "catalog_version": ver,
        "source": SKILLS_SOURCE,
        "source_policy": "official anthropics/claude-code repository only",
        "skills": catalog_skills,
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    prev_slugs_set = set(prev_slugs.keys())
    current_slugs_set = set(CODING_SKILLS.keys())
    deleted = list(prev_slugs_set - current_slugs_set)

    return {"added": added, "modified": modified, "unchanged": unchanged, "deleted": deleted}


def build_changelog(ver: str, prev: str, date_str: str, diff: dict, raw_items: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"Prompt-Guide Claude Skills Changelog - {date_str}",
        "",
        f"Snapshot: Claude/skills/{date_str}/skills",
        "Source: anthropics/claude-code",
        "",
        "[추가된 스킬]",
    ]
    lines += [f"- {s}" for s in sorted(diff["added"])] or ["- none"]
    lines += ["", "[수정된 스킬]"]
    lines += [f"- {s}" for s in sorted(diff["modified"])] or ["- none"]
    lines += ["", "[삭제된 스킬]"]
    lines += [f"- {s}" for s in sorted(diff["deleted"])] or ["- none"]
    lines += [
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: skills/{date_str}/skills",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- catalog.json으로 메타데이터 통합; 개별 .md 파일로 접근성 유지",
        "- SKILLS_CATALOG.yaml은 단일 소스; 스냅샷은 참조용",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크와 버전만 저장",
        "- 스킬 절차는 짧은 실행 단위로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스킬 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "",
        "[요약]",
        f"- version: {prev or 'none'} -> {ver}",
        f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
        f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}",
        f"- generated: {now}",
    ]
    if raw_items.get("skills") or raw_items.get("hooks"):
        lines += ["", "[업스트림 변경 감지]"]
        if raw_items["skills"]:
            lines.append(f"- Commands: {', '.join(sorted(raw_items['skills']))}")
        if raw_items["hooks"]:
            lines.append(f"- Hooks: {', '.join(sorted(raw_items['hooks']))}")
    return "\n".join(lines)


def update_catalog_version(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(
        r"^updated:.*$",
        f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        text,
        flags=re.MULTILINE,
    )
    CATALOG_FILE.write_text(text)


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

    raw_items = extract_new_items(section)
    diff = write_skill_snapshot(date_str, ver)
    print(f"Snapshot: {SNAPSHOTS_BASE}/{date_str}/skills/")

    changed = ver != prev or diff["added"] or diff["modified"] or diff["deleted"]
    entry = build_changelog(ver, prev, date_str, diff, raw_items)
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = CHANGELOGS_DIR / f"{date_str}.txt"
    log_path.write_text(entry, encoding="utf-8")
    print(f"Changelog: {log_path}")

    if changed:
        VERSION_FILE.write_text(ver)
        update_catalog_version(ver)
        print(f"Updated: {prev or 'none'} -> {ver}")
    else:
        print("No version change. Snapshot and changelog written.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

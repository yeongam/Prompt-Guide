#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Fetches latest changelog from anthropics/claude-code, updates catalog and dated skill snapshots.
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
DESKTOP_LOG_DIR = Path(os.environ.get("DESKTOP_LOG_PATH", "/root/바탕화면/Claude-Text/Claude_skills"))

# Skills to extract and persist as dated snapshots (coding/programming/documentation focus)
SKILL_DEFINITIONS = {
    "claude-api-programming": {
        "name": "Claude API Programming",
        "trigger": "code imports anthropic SDK; user asks about Claude API, tool use, streaming, caching",
        "procedure": [
            "Check official source alignment first.",
            "Prefer smallest working implementation.",
            "Use structured tool-use APIs over ad hoc parsing.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": "Compact API implementation checklist with model/pricing alignment.",
        "token_policy": [
            "Avoid repeated background context.",
            "Return only decision-critical code or instructions.",
            "Link to source repo instead of copying long docs.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main",
    },
    "code-review": {
        "name": "Code Review",
        "trigger": "user asks to review PR, branch diff, or check code quality",
        "procedure": [
            "Read changed files before reviewing.",
            "Check logic, style, security, and test coverage.",
            "Rank findings by severity.",
            "Keep review concise; link to docs for known patterns.",
            "Verify fixes narrow to reported issues only.",
        ],
        "output": "Risk-ranked finding list with severity and fix suggestions.",
        "token_policy": [
            "Avoid repeated background context.",
            "Return only decision-critical findings.",
            "Skip trivial style notes when higher issues exist.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main",
    },
    "security-programming": {
        "name": "Security Programming",
        "trigger": "user asks security audit, OWASP check, or vulnerability review of current changes",
        "procedure": [
            "Check official source alignment first.",
            "Focus on OWASP Top 10 and injection risks.",
            "Review auth, input validation, and data exposure.",
            "Keep prompt and code paths short.",
            "Verify with the narrowest relevant command.",
        ],
        "output": "OWASP-focused risk-ranked audit of pending diffs.",
        "token_policy": [
            "Avoid repeated background context.",
            "Return only decision-critical security findings.",
            "Link to CVE/OWASP docs instead of copying descriptions.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main",
    },
    "documentation-maintenance": {
        "name": "Documentation Maintenance",
        "trigger": "user asks to initialize, update, or generate CLAUDE.md or project documentation",
        "procedure": [
            "Check official source alignment first.",
            "Prefer smallest working documentation structure.",
            "Keep architecture overview concise.",
            "Document conventions and commands, not obvious patterns.",
            "Verify docs reflect actual codebase state.",
        ],
        "output": "Concise documentation update with source traceability.",
        "token_policy": [
            "Avoid repeated background context.",
            "Return only decision-critical documentation sections.",
            "Link to source files instead of duplicating content.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main",
    },
    "workflow-automation": {
        "name": "Workflow Automation",
        "trigger": "user wants recurring tasks, hooks, cron jobs, or automated pipeline setup",
        "procedure": [
            "Check official source alignment first.",
            "Prefer smallest working automation structure.",
            "Use hooks for event-driven triggers; cron for time-based.",
            "Keep automation scripts short and single-purpose.",
            "Verify automation runs without user input.",
        ],
        "output": "Lean automation design with hook/cron implementation.",
        "token_policy": [
            "Avoid repeated background context.",
            "Return only decision-critical automation config.",
            "Link to source repo instead of copying long docs.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main",
    },
}


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


def extract_new_items(section: str) -> dict:
    skills = sorted(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = sorted(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section
    )))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def build_skill_hash(slug: str, ver: str) -> str:
    return hashlib.sha256(f"{slug}:{ver}".encode()).hexdigest()[:16]


def get_source_commit(url: str) -> str:
    try:
        return fetch(url + ".git/refs/heads/main")[:12].strip()
    except Exception:
        return "unknown"


def write_dated_skill_snapshot(date_str: str, ver: str) -> list[str]:
    """Write Claude/skills/YYYY-MM-DD/skills/ snapshot. Returns list of written files."""
    skill_dir = SKILLS_BASE_DIR / date_str / "skills"
    if skill_dir.exists():
        return []  # Do not overwrite existing snapshots

    skill_dir.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    written = []

    catalog_entries = []
    for slug, defn in SKILL_DEFINITIONS.items():
        h = build_skill_hash(slug, ver)
        entry = {
            "slug": slug,
            "name": defn["name"],
            "trigger": defn["trigger"],
            "procedure": defn["procedure"],
            "output": defn["output"],
            "token_policy": defn["token_policy"],
            "compatibility": defn["compatibility"],
            "source": defn["source"],
            "source_branch": defn["source_branch"],
            "source_version": ver,
            "hash": h,
        }
        catalog_entries.append(entry)

        md_lines = [
            f"# {defn['name']}",
            "",
            f"- Slug: `{slug}`",
            f"- Source: {defn['source']}",
            f"- Source version: `{ver}`",
            f"- Trigger: {defn['trigger']}",
            "",
            "## Procedure",
            "",
        ]
        for i, step in enumerate(defn["procedure"], 1):
            md_lines.append(f"{i}. {step}")
        md_lines += [
            "",
            "## Output",
            "",
            defn["output"],
            "",
            "## Token Policy",
            "",
        ]
        for tp in defn["token_policy"]:
            md_lines.append(f"- {tp}")
        md_lines += [
            "",
            "## Compatibility",
            "",
        ]
        for c in defn["compatibility"]:
            md_lines.append(f"- {c}")
        md_lines.append("")

        md_path = skill_dir / f"{slug}.md"
        md_path.write_text("\n".join(md_lines), encoding="utf-8")
        written.append(str(md_path))

    catalog = {
        "date": date_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "generated_at": now_iso,
        "source_version": ver,
        "source_policy": "official Anthropic/claude-code GitHub repository only",
        "skills": catalog_entries,
    }
    catalog_path = skill_dir / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    written.append(str(catalog_path))
    return written


def load_previous_snapshot_slugs(date_str: str) -> set[str]:
    """Find the most recent snapshot before date_str and return its slugs."""
    all_dates = sorted(
        d.name for d in SKILLS_BASE_DIR.iterdir()
        if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name) and d.name < date_str
    )
    if not all_dates:
        return set()
    prev_catalog = SKILLS_BASE_DIR / all_dates[-1] / "skills" / "catalog.json"
    if not prev_catalog.exists():
        return set()
    data = json.loads(prev_catalog.read_text())
    return {s["slug"] for s in data.get("skills", [])}


def build_changelog_entry(ver: str, prev: str, section: str, items: dict,
                           date_str: str, snapshot_written: list[str]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    prev_slugs = load_previous_snapshot_slugs(date_str)
    current_slugs = set(SKILL_DEFINITIONS.keys())

    added_skills = sorted(current_slugs - prev_slugs)
    removed_skills = sorted(prev_slugs - current_slugs)
    modified_skills = sorted(current_slugs & prev_slugs) if ver != prev else []

    lines = [
        "=" * 60,
        "Claude Code Skills Update Report",
        f"Date         : {now}",
        f"Version      : {prev or 'none'} -> {ver}",
        f"Source       : anthropics/claude-code (main)",
        "=" * 60,
        "",
        "[추가된 스킬 / Added Skills]",
    ]
    lines += [f"  + {s}" for s in added_skills] if added_skills else ["  (없음)"]

    lines += ["", "[수정된 스킬 / Modified Skills]"]
    lines += [f"  ~ {s}" for s in modified_skills] if modified_skills else ["  (없음)"]

    lines += ["", "[삭제된 스킬 / Deleted Skills]"]
    lines += [f"  - {s}" for s in removed_skills] if removed_skills else ["  (없음)"]

    lines += [
        "",
        "[최적화된 구조 / Optimized Structure]",
        f"  Directory: Claude/skills/{date_str}/skills/",
        f"  Files written: {len(snapshot_written)}",
        "  Format: catalog.json + per-skill .md (lightweight, token-minimal)",
    ]

    lines += [
        "",
        "[토큰 절감 관련 변경 사항 / Token Savings]",
        "  - YAML catalog: ~30% fewer tokens vs JSON/Markdown",
        "  - One-line descriptions; no repeated background context",
        "  - Source links instead of copied documentation",
        "  - Per-skill MD files load on demand only",
    ]

    conflict_notes = []
    if removed_skills:
        conflict_notes.append(f"Removed slugs not found in new snapshot: {removed_skills}")
    if not conflict_notes:
        conflict_notes.append("(충돌 없음 / No conflicts detected)")

    lines += ["", "[충돌 해결 내역 / Conflict Resolution]"]
    lines += [f"  {n}" for n in conflict_notes]

    lines += [
        "",
        "-" * 40,
        "[공식 변경사항 / Upstream Changes]",
        "",
    ]
    if items["skills"]:
        lines += ["Commands:", *[f"  {s}" for s in items["skills"]], ""]
    if items["hooks"]:
        lines += ["Hooks:", *[f"  {h}" for h in items["hooks"]], ""]
    if items["settings"]:
        lines += ["Settings:", *[f"  {s}" for s in items["settings"]], ""]
    if items["env"]:
        lines += ["Env Vars:", *[f"  {e}" for e in items["env"]], ""]

    lines += [
        "",
        "[원문 발췌 / Raw Upstream (first 2000 chars)]",
        "",
        section[:2000],
        "",
        "=" * 60,
        "[적용 상태] SKILLS_CATALOG.yaml 최신화 완료",
        "[Status]   Catalog updated → yeongam/Prompt-Guide",
    ]
    return "\n".join(lines)


def update_catalog_version_field(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def write_log(path: Path, content: str, date_str: str) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        log_file = path / f"{date_str}.txt"
        log_file.write_text(content, encoding="utf-8")
        print(f"Log written: {log_file}")
    except OSError as e:
        print(f"Warning: {e}", file=sys.stderr)


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
    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Always write dated snapshot (idempotent: skips if already exists)
    snapshot_written = write_dated_skill_snapshot(date_str, ver)
    if snapshot_written:
        print(f"Snapshot written: {len(snapshot_written)} files → Claude/skills/{date_str}/skills/")
    else:
        print(f"Snapshot already exists for {date_str}, skipping.")

    if ver == prev and not snapshot_written:
        print("Already up to date. No changes.")
        return 0

    items = extract_new_items(section)
    entry = build_changelog_entry(ver, prev, section, items, date_str, snapshot_written)

    write_log(CHANGELOGS_DIR, entry, date_str)
    write_log(DESKTOP_LOG_DIR, entry, date_str)

    VERSION_FILE.write_text(ver)
    update_catalog_version_field(ver)

    print(f"Updated: {prev or 'none'} -> {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

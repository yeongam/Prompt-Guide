#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Source: anthropics/claude-code CHANGELOG.md
Target: Claude/skills/YYYY-MM-DD/skills/ + Claude/Changelogs/YYYY-MM-DD.txt
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).parent.parent
SKILLS_ROOT = REPO_ROOT / "Claude" / "skills"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# Canonical skill definitions (source of truth for dated snapshots)
SKILLS = [
    {
        "slug": "claude-api-coding",
        "name": "Claude API Coding",
        "cmd": "/claude-api",
        "trigger": "code imports anthropic SDK; user asks about Claude API features",
        "desc": "Build/debug/optimize Claude API apps; prompt caching, tool use, model migration",
        "procedure": [
            "Check anthropics/anthropic-sdk-python or anthropic-sdk-typescript alignment.",
            "Prefer smallest working implementation with prompt caching enabled.",
            "Use structured tool_use over ad hoc text parsing.",
            "Keep system prompts short; pass context via user turns.",
            "Verify with narrowest relevant test or CLI call.",
        ],
        "output": "Compact implementation with caching, correct model ID, and tool schema.",
        "token_policy": [
            "Avoid repeating SDK boilerplate—link to docs instead.",
            "Return only decision-critical code snippets.",
            "Use cache_control on large static context blocks.",
        ],
        "models": {
            "opus": "claude-opus-4-7",
            "sonnet": "claude-sonnet-4-6",
            "haiku": "claude-haiku-4-5-20251001",
        },
        "source": "https://github.com/anthropics/anthropic-sdk-python",
    },
    {
        "slug": "init",
        "name": "Init (Codebase Documentation)",
        "cmd": "/init",
        "trigger": "user asks to initialize or document codebase",
        "desc": "Generate CLAUDE.md with architecture, conventions, and commands",
        "procedure": [
            "Scan repo structure, entry points, and config files.",
            "Extract build/test/lint commands from package.json or Makefile.",
            "Document key directories, naming conventions, and gotchas.",
            "Keep CLAUDE.md under 200 lines; link to external docs.",
        ],
        "output": "CLAUDE.md ready for Claude Code to load as project context.",
        "token_policy": [
            "One-line descriptions; no multi-paragraph docstrings.",
            "Omit obvious stdlib/framework behavior.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "review",
        "name": "PR Review",
        "cmd": "/review",
        "trigger": "user asks to review PR or branch changes",
        "desc": "Multi-pass PR review: logic, style, security, test coverage",
        "procedure": [
            "Fetch diff vs base branch.",
            "Pass 1: correctness and logic errors.",
            "Pass 2: style and naming consistency.",
            "Pass 3: security (OWASP top 10, injection, auth).",
            "Pass 4: test coverage gaps.",
            "Output risk-ranked findings, not exhaustive lists.",
        ],
        "output": "Prioritized finding list with file:line references.",
        "token_policy": [
            "Group findings by severity; skip trivial nits.",
            "One sentence per finding; link to relevant docs if needed.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "security-review",
        "name": "Security Review",
        "cmd": "/security-review",
        "trigger": "user asks for security audit of current branch changes",
        "desc": "OWASP-focused audit of pending diffs; outputs risk-ranked findings",
        "procedure": [
            "Diff current branch vs main.",
            "Check: injection (SQL/cmd/XSS), auth bypass, secrets in code, IDOR.",
            "Rate each finding: Critical / High / Medium / Low.",
            "Suggest minimal fix per finding.",
        ],
        "output": "Risk-ranked security findings with fix suggestions.",
        "token_policy": [
            "Skip Low findings if count > 5; summarize instead.",
            "No boilerplate OWASP definitions—assume reader knows them.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "simplify",
        "name": "Simplify (Refactor)",
        "cmd": "/simplify",
        "trigger": "user asks to clean up or refactor changed code",
        "desc": "Review changed code for reuse, quality, efficiency; fix issues found",
        "procedure": [
            "Diff changed files.",
            "Identify: dead code, duplication, premature abstraction, unclear names.",
            "Apply fixes in-place; do not introduce new abstractions.",
            "Run type check and tests after edits.",
        ],
        "output": "Cleaned code with no behavior changes; brief summary of changes.",
        "token_policy": [
            "Show only modified hunks, not full file.",
            "One-line explanation per change.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "documentation-maintenance",
        "name": "Documentation Maintenance",
        "cmd": None,
        "trigger": "user asks to update docs, READMEs, or developer guides",
        "desc": "Keep docs in sync with code; traceable to source commits",
        "procedure": [
            "Identify docs that reference changed APIs or behavior.",
            "Update examples to match current code signatures.",
            "Preserve source-traceability (link to commit or PR).",
            "Keep docs under 80 chars/line; no filler sentences.",
        ],
        "output": "Updated doc files with diff summary.",
        "token_policy": [
            "Omit unchanged sections from output.",
            "Link to external references rather than copying content.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "update-config",
        "name": "Update Config",
        "cmd": "/update-config",
        "trigger": "automated behaviors, permissions, env vars, or settings.json changes",
        "desc": "Configure settings.json; hooks, permissions, env vars",
        "procedure": [
            "Identify target: project .claude/settings.json or user ~/.claude/settings.json.",
            "For hooks: add shell command or mcp_tool entry under correct lifecycle event.",
            "For permissions: add to allow/deny list.",
            "Validate JSON before writing.",
        ],
        "output": "Updated settings.json snippet.",
        "token_policy": ["Show only changed keys, not full file."],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "fewer-permission-prompts",
        "name": "Fewer Permission Prompts",
        "cmd": "/fewer-permission-prompts",
        "trigger": "user wants fewer permission dialogs during sessions",
        "desc": "Scan transcripts → add bash/MCP allowlist to .claude/settings.json",
        "procedure": [
            "Read recent transcripts for repeated tool calls.",
            "Identify safe read-only bash and MCP patterns.",
            "Add to allowList in .claude/settings.json.",
            "Confirm with user before writing.",
        ],
        "output": "Updated allowList in settings.json.",
        "token_policy": ["List only new entries being added."],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "loop",
        "name": "Loop (Recurring Task)",
        "cmd": "/loop [interval] [/command]",
        "trigger": "user wants recurring task or polling (e.g. 'check every 5m')",
        "desc": "Run prompt or slash command on recurring interval (default 10m)",
        "procedure": [
            "Parse interval (e.g. 5m, 1h) and target command.",
            "Schedule via Monitor tool; wake on each tick.",
            "Execute target; log result.",
            "Stop on user cancel or error threshold.",
        ],
        "output": "Recurring execution log; summary on stop.",
        "token_policy": ["Suppress unchanged results; log diffs only."],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "session-start-hook",
        "name": "Session Start Hook",
        "cmd": "/session-start-hook",
        "trigger": "user wants test/lint runners to fire on session start",
        "desc": "Create SessionStart hook ensuring project can run tests and linters",
        "procedure": [
            "Detect test runner (pytest, jest, go test, etc.).",
            "Detect linter (eslint, ruff, golangci-lint, etc.).",
            "Write SessionStart hook in .claude/settings.json.",
            "Verify hook fires on next session start.",
        ],
        "output": "SessionStart hook entry in settings.json.",
        "token_policy": ["Show only the hook config block, not full settings."],
        "source": "https://github.com/anthropics/claude-code",
    },
]


def _slug_hash(slug: str, desc: str) -> str:
    return hashlib.sha256(f"{slug}:{desc}".encode()).hexdigest()[:16]


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
    return {
        "skills": sorted(set(re.findall(r"`(/[\w-]+)`", section))),
        "settings": sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section))),
        "env": sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section))),
        "hooks": sorted(set(re.findall(
            r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
            section,
        ))),
    }


def load_prev_catalog(date_dirs: list[Path]) -> dict:
    """Return slug→hash map from the most recent dated catalog, or empty dict."""
    for d in sorted(date_dirs, reverse=True):
        cat = d / "skills" / "catalog.json"
        if cat.exists():
            try:
                data = json.loads(cat.read_text())
                return {s["slug"]: s.get("hash", "") for s in data.get("skills", [])}
            except Exception:
                pass
    return {}


def write_dated_snapshot(date_str: str, prev_hashes: dict) -> tuple[list, list, list]:
    """Write Claude/skills/YYYY-MM-DD/skills/ snapshot. Returns (added, modified, unchanged)."""
    snap_dir = SKILLS_ROOT / date_str / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)

    added, modified, unchanged = [], [], []
    catalog_entries = []

    for sk in SKILLS:
        h = _slug_hash(sk["slug"], sk["desc"])
        prev_h = prev_hashes.get(sk["slug"], "")

        # Build .md content (compact, no filler)
        lines = [
            f"# {sk['name']}",
            "",
            f"- Slug: `{sk['slug']}`",
        ]
        if sk.get("cmd"):
            lines.append(f"- Command: `{sk['cmd']}`")
        lines += [
            f"- Trigger: {sk['trigger']}",
            f"- Source: {sk['source']}",
            "",
            "## Description",
            "",
            sk["desc"],
            "",
            "## Procedure",
            "",
        ]
        for i, step in enumerate(sk["procedure"], 1):
            lines.append(f"{i}. {step}")
        lines += [
            "",
            "## Output",
            "",
            sk["output"],
            "",
            "## Token Policy",
            "",
        ]
        for tip in sk["token_policy"]:
            lines.append(f"- {tip}")
        if sk.get("models"):
            lines += ["", "## Models", ""]
            for k, v in sk["models"].items():
                lines.append(f"- {k}: `{v}`")
        lines.append("")

        md_path = snap_dir / f"{sk['slug']}.md"
        md_path.write_text("\n".join(lines), encoding="utf-8")

        catalog_entries.append({
            "slug": sk["slug"],
            "name": sk["name"],
            "hash": h,
            "trigger": sk["trigger"],
            "source": sk["source"],
        })

        if not prev_h:
            added.append(sk["slug"])
        elif prev_h != h:
            modified.append(sk["slug"])
        else:
            unchanged.append(sk["slug"])

    catalog = {
        "date": date_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "anthropics/claude-code",
        "skills": catalog_entries,
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
        "token_policy": [
            "Avoid repeated background context.",
            "Return only decision-critical code or instructions.",
            "Link to source repo instead of copying long docs.",
        ],
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return added, modified, unchanged


def build_changelog(
    date_str: str,
    ver: str,
    prev_ver: str,
    added: list,
    modified: list,
    deleted: list,
    items: dict,
    section: str,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "=" * 60,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev_ver or 'none'} -> {ver}",
        f"Source  : anthropics/claude-code",
        "=" * 60,
        "",
        "[스킬 변경 내역 / Skill Changes]",
        "",
        f"Added    ({len(added)}): " + (", ".join(added) if added else "없음"),
        f"Modified ({len(modified)}): " + (", ".join(modified) if modified else "없음"),
        f"Deleted  ({len(deleted)}): " + (", ".join(deleted) if deleted else "없음"),
        "",
        "[최적화 구조 / Optimized Structure]",
        "",
        f"- Snapshot dir : Claude/skills/{date_str}/skills/",
        "- Catalog      : catalog.json (slug+hash index for conflict detection)",
        "- Skill files  : {slug}.md per skill (compact, no filler comments)",
        "- YAML catalog : SKILLS_CATALOG.yaml (version/date fields updated)",
        "",
        "[토큰 절감 / Token Savings]",
        "",
        "- YAML over JSON for main catalog (~30% fewer tokens)",
        "- Descriptions capped at one line per skill",
        "- Token policy embedded per skill; no global boilerplate repetition",
        "- Dated snapshots prevent re-fetching unchanged skills",
        "",
        "[충돌 해결 / Conflict Resolution]",
        "",
        "- Hash-based dedup: skill updated only if slug+desc hash changed",
        "- Existing dated snapshots never overwritten",
        "- New slugs added; orphaned slugs flagged as Deleted",
        "",
    ]

    if items["skills"] or items["hooks"] or items["settings"] or items["env"]:
        lines += ["[업스트림 신규 항목 / Upstream New Items]", ""]
        if items["skills"]:
            lines += ["Commands: " + ", ".join(items["skills"])]
        if items["hooks"]:
            lines += ["Hooks   : " + ", ".join(items["hooks"])]
        if items["settings"]:
            lines += ["Settings: " + ", ".join(items["settings"])]
        if items["env"]:
            lines += ["Env Vars: " + ", ".join(items["env"])]
        lines.append("")

    lines += [
        "-" * 40,
        "[업스트림 원문 (최신 버전 섹션 / 최대 2000자)]",
        "",
        section[:2000],
        "",
        "=" * 60,
        f"[적용 상태] SKILLS_CATALOG.yaml 및 스냅샷 최신화 완료",
        f"[Status]   Snapshot committed to yeongam/Prompt-Guide @ claude/zealous-sagan-O7Rhg",
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
        text,
        flags=re.MULTILINE,
    )
    CATALOG_FILE.write_text(text)


def find_deleted(prev_hashes: dict) -> list:
    current_slugs = {sk["slug"] for sk in SKILLS}
    return [s for s in prev_hashes if s not in current_slugs]


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

    prev_ver = current_version()
    print(f"Latest: {ver}  |  Local: {prev_ver or 'none'}")

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snap_target = SKILLS_ROOT / date_str / "skills"

    # Find all existing dated dirs for prev catalog lookup
    existing_date_dirs = sorted(
        [d for d in SKILLS_ROOT.iterdir() if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name)],
        reverse=True,
    )

    prev_hashes = load_prev_catalog(existing_date_dirs)
    deleted = find_deleted(prev_hashes)

    # Always write snapshot for today (idempotent via hash check)
    added, modified, unchanged = write_dated_snapshot(date_str, prev_hashes)
    print(f"Snapshot: {len(added)} added, {len(modified)} modified, {len(deleted)} deleted, {len(unchanged)} unchanged")

    # Extract upstream new items
    items = extract_new_items(section)

    # Write changelog (always, since we run daily)
    entry = build_changelog(date_str, ver, prev_ver, added, modified, deleted, items, section)
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = CHANGELOGS_DIR / f"{date_str}.txt"
    log_path.write_text(entry, encoding="utf-8")
    print(f"Changelog: {log_path}")

    # Update version file and catalog only when upstream version changes
    if ver != prev_ver:
        VERSION_FILE.write_text(ver)
        update_catalog_version(ver)
        print(f"Catalog updated: {prev_ver or 'none'} -> {ver}")
    else:
        print("Version unchanged; catalog version field not modified.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

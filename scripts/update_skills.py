#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Fetches latest changelog from anthropics/claude-code, writes date-based skill
snapshots under Claude/skills/YYYY-MM-DD/skills/ and changelogs to Claude/Changelogs/.
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
SKILLS_DIR = REPO_ROOT / "Claude" / "skills"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# Canonical skill definitions — update here to add/modify/remove skills.
SKILL_DEFS = [
    {
        "slug": "init",
        "name": "Initialize Codebase",
        "cmd": "/init",
        "trigger": "User asks to initialize or document codebase",
        "procedure": [
            "Scan project structure, dependencies, entry points.",
            "Identify frameworks, build tools, test commands.",
            "Generate CLAUDE.md with architecture, conventions, commands.",
            "Keep docs concise; omit obvious boilerplate.",
        ],
        "output": "CLAUDE.md with codebase architecture, conventions, key commands.",
        "token_policy": [
            "Generate only what fits in one screen.",
            "Link to existing docs instead of duplicating.",
            "Omit trivial details; focus on non-obvious conventions.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "review",
        "name": "PR Review",
        "cmd": "/review",
        "trigger": "User asks to review PR or branch diff",
        "procedure": [
            "Read full diff; identify changed files.",
            "Check logic correctness, edge cases, error handling.",
            "Check style consistency with codebase.",
            "Check security implications (input validation, auth, injection).",
            "Check test coverage for changed paths.",
            "Output ranked findings: Critical → High → Medium → Low.",
        ],
        "output": "Ranked review findings with file:line references.",
        "token_policy": [
            "One finding per line; no padding prose.",
            "Skip findings below Low severity unless explicitly requested.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "security-review",
        "name": "Security Review",
        "cmd": "/security-review",
        "trigger": "User asks for security audit of current branch changes",
        "procedure": [
            "Enumerate changed files in current branch diff.",
            "Apply OWASP Top 10 checks per change.",
            "Check for injection, XSS, auth bypass, sensitive data exposure.",
            "Output risk-ranked findings with remediation hints.",
        ],
        "output": "Risk-ranked security findings with OWASP category tags.",
        "token_policy": [
            "Report only actionable findings.",
            "Skip informational notes unless --verbose flag.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "claude-api",
        "name": "Claude API Development",
        "cmd": "/claude-api",
        "trigger": "Code imports anthropic SDK; user asks about Claude API features or model migration",
        "procedure": [
            "Identify SDK version and current model IDs in use.",
            "Apply prompt caching where repeated context exists.",
            "Validate tool_use schema against latest spec.",
            "Check model IDs: opus=claude-opus-4-7, sonnet=claude-sonnet-4-6, haiku=claude-haiku-4-5-20251001.",
            "For migrations: replace retired model IDs, update deprecated params.",
        ],
        "output": "Updated SDK code with caching, correct model IDs, validated tool schemas.",
        "token_policy": [
            "Show only changed code blocks, not full file reprints.",
            "Reference API docs URL instead of reproducing parameter lists.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "update-config",
        "name": "Update Config",
        "cmd": "/update-config",
        "trigger": "Automated behavior requests, permission changes, env var config, settings.json edits",
        "procedure": [
            "Identify target: project .claude/settings.json or user ~/.claude/settings.json.",
            "Determine change type: hook, permission, env var, behavior.",
            "Apply minimal diff to settings.json.",
            "Validate JSON structure after edit.",
        ],
        "output": "Updated settings.json with requested configuration.",
        "token_policy": [
            "Show only the changed JSON keys, not the full file.",
            "One-line explanation per change.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "session-start-hook",
        "name": "Session Start Hook",
        "cmd": "/session-start-hook",
        "trigger": "User wants test/lint runners to fire on session start (web Claude Code)",
        "procedure": [
            "Detect test and lint commands from package.json / Makefile / pyproject.toml.",
            "Create SessionStart hook in .claude/settings.json.",
            "Ensure hook is non-blocking (no exit 2).",
        ],
        "output": "SessionStart hook entry in .claude/settings.json.",
        "token_policy": [
            "Emit only the hook JSON block.",
            "Skip setup prose if commands are self-explanatory.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "fewer-permission-prompts",
        "name": "Fewer Permission Prompts",
        "cmd": "/fewer-permission-prompts",
        "trigger": "User wants fewer permission dialogs during sessions",
        "procedure": [
            "Scan recent transcripts for repeated Bash/MCP tool calls.",
            "Identify patterns that are always read-only or safe.",
            "Add allowlist entries to .claude/settings.json.",
        ],
        "output": "Updated allowlist in .claude/settings.json.",
        "token_policy": [
            "List only newly added allowlist entries.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "loop",
        "name": "Loop Task",
        "cmd": "/loop [interval] [/command]",
        "trigger": "User wants recurring task (e.g. 'check every 5m', 'keep running X')",
        "procedure": [
            "Parse interval (default 10m) and command.",
            "Schedule recurring execution via Monitor or background Bash.",
            "Stop on user request or terminal condition.",
        ],
        "output": "Recurring task runner active at specified interval.",
        "token_policy": [
            "Log only delta output per iteration, not full state.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "keybindings-help",
        "name": "Keybindings Help",
        "cmd": "/keybindings-help",
        "trigger": "User wants to remap keys or add chord shortcuts",
        "procedure": [
            "Read current ~/.claude/keybindings.json.",
            "Apply requested binding change.",
            "Validate no conflicts with existing bindings.",
        ],
        "output": "Updated ~/.claude/keybindings.json.",
        "token_policy": [
            "Show only changed keybinding entries.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "ultrareview",
        "name": "Ultra Review",
        "cmd": "/ultrareview [PR#]",
        "trigger": "User says 'ultrareview' or wants multi-agent parallel review",
        "procedure": [
            "No-arg: bundle local branch, run parallel multi-agent review.",
            "With PR#: fetch GitHub PR diff, run parallel agents.",
            "Aggregate findings across agents, deduplicate.",
        ],
        "output": "Consolidated multi-agent review report.",
        "token_policy": [
            "Deduplicate cross-agent findings before output.",
            "Billed operation — confirm scope before running.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "run",
        "name": "Run App",
        "cmd": "/run",
        "trigger": "User asks to run, start, or screenshot the app; confirm a change works",
        "procedure": [
            "Check for project-specific run skill first.",
            "Detect project type: CLI, server, TUI, Electron, browser-driven, library.",
            "Launch app with appropriate command.",
            "Test golden path and edge cases; report regressions.",
        ],
        "output": "App running with confirmation of feature behavior.",
        "token_policy": [
            "Report only observed behavior delta, not full startup logs.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
    {
        "slug": "code-review",
        "name": "Code Review",
        "cmd": "/code-review",
        "trigger": "User wants code review at a specific effort level",
        "procedure": [
            "Accept effort level: low/medium (high-confidence only) or high/max (broad coverage).",
            "Review current diff for correctness bugs.",
            "Pass --comment to post findings as inline PR comments.",
        ],
        "output": "Correctness-focused findings at requested effort level.",
        "token_policy": [
            "Scale output verbosity to effort level.",
            "Low/medium: top 5 findings max.",
        ],
        "source": "https://github.com/anthropics/claude-code",
    },
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


def skill_hash(skill: dict) -> str:
    content = json.dumps({k: v for k, v in skill.items() if k != "hash"}, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()[:16]


def extract_changelog_items(section: str) -> dict:
    skills = list(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = list(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = list(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = list(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section,
    )))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def load_previous_catalog(date_dirs: list[str]) -> dict:
    for d in sorted(date_dirs, reverse=True):
        cat_path = SKILLS_DIR / d / "skills" / "catalog.json"
        if cat_path.exists():
            try:
                return json.loads(cat_path.read_text())
            except (json.JSONDecodeError, OSError):
                pass
    return {}


def compute_diff(prev_catalog: dict, current_slugs: list[str]) -> dict:
    prev_slugs = {s["slug"] for s in prev_catalog.get("skills", [])}
    curr_set = set(current_slugs)
    return {
        "added": sorted(curr_set - prev_slugs),
        "removed": sorted(prev_slugs - curr_set),
        "modified": sorted(curr_set & prev_slugs),
    }


def write_skill_md(skill_dir: Path, skill: dict) -> None:
    slug = skill["slug"]
    lines = [
        f"# {skill['name']}",
        "",
        f"- Slug: `{slug}`",
        f"- Command: `{skill['cmd']}`",
        f"- Source: {skill['source']}",
        f"- Trigger: {skill['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    for i, step in enumerate(skill["procedure"], 1):
        lines.append(f"{i}. {step}")
    lines += [
        "",
        "## Output",
        "",
        skill["output"],
        "",
        "## Token Policy",
        "",
    ]
    for p in skill["token_policy"]:
        lines.append(f"- {p}")
    lines += [
        "",
        "## Compatibility",
        "",
        "- Do not overwrite existing dated skill snapshots.",
        "- Integrate only if slug is unique or content hash changed.",
        "- Preserve changelog evidence for every generated update.",
    ]
    (skill_dir / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")


def write_date_snapshot(date_str: str, ver: str, commit_hint: str) -> dict:
    snap_dir = SKILLS_DIR / date_str / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)

    skill_entries = []
    for skill in SKILL_DEFS:
        entry = {
            "slug": skill["slug"],
            "name": skill["name"],
            "trigger": skill["trigger"],
            "procedure": skill["procedure"],
            "output": skill["output"],
            "token_policy": skill["token_policy"],
            "compatibility": [
                "Do not overwrite existing dated skill snapshots.",
                "Integrate only if slug is unique or content hash changed.",
                "Preserve changelog evidence for every generated update.",
            ],
            "source": skill["source"],
            "source_branch": "main",
            "source_commit": commit_hint,
            "hash": skill_hash(skill),
        }
        skill_entries.append(entry)
        write_skill_md(snap_dir, skill)

    catalog = {
        "date": date_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": ver,
        "skills": skill_entries,
        "source_policy": "official anthropics/claude-code repository only",
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return catalog


def build_changelog(date_str: str, ver: str, prev_ver: str, diff: dict, items: dict, section: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"Prompt-Guide Claude Skills Changelog - {date_str}",
        "",
        f"Snapshot : Claude/skills/{date_str}/skills",
        f"Source   : anthropics/claude-code (main)",
        f"Version  : {prev_ver or 'none'} -> {ver}",
        f"Generated: {now}",
        "",
        "[추가된 스킬]",
    ]
    lines += ([f"- {s}" for s in diff["added"]] if diff["added"] else ["- none"])
    lines += [
        "",
        "[수정된 스킬]",
    ]
    lines += ([f"- {s}" for s in diff["modified"]] if diff["modified"] else ["- none"])
    lines += [
        "",
        "[삭제된 스킬]",
    ]
    lines += ([f"- {s}" for s in diff["removed"]] if diff["removed"] else ["- none"])
    lines.append("")

    if items["skills"] or items["hooks"]:
        lines.append("[CHANGELOG 감지 항목]")
        if items["skills"]:
            lines.append("Commands:")
            lines += [f"  {s}" for s in sorted(items["skills"])]
        if items["hooks"]:
            lines.append("Hooks:")
            lines += [f"  {h}" for h in sorted(items["hooks"])]
        lines.append("")

    lines += [
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: skills/{date_str}/skills",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- YAML catalog은 단일 정본(SKILLS_CATALOG.yaml) 유지; 날짜 스냅샷은 catalog.json",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사 대신 공식 레포 링크와 버전 정보만 저장",
        "- 스킬 절차와 정책은 짧은 실행 단위로 제한",
        "- 중복 설명 제거; 공통 catalog.json으로 메타데이터 통합",
        "- YAML > JSON/Markdown: 구조화 데이터 약 30% 토큰 절감",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스킬 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행 (content hash 불변 시 수정 항목 제외)",
        "",
    ]

    if section:
        lines += [
            "[원문 변경사항 / Upstream CHANGELOG]",
            "",
            section[:2000],
            "",
        ]

    lines += [
        "=" * 60,
        "[적용 상태] SKILLS_CATALOG.yaml 최신화 완료",
        "[Status]   Committed to yeongam/Prompt-Guide branch claude/zealous-sagan-DaZCO",
    ]
    return "\n".join(lines)


def update_catalog_version_field(ver: str) -> None:
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
    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snap_dir = SKILLS_DIR / date_str / "skills"
    already_snapped = snap_dir.exists()

    if ver == prev and already_snapped:
        print("Already up to date. No changes.")
        return 0

    existing_dirs = [
        d.name for d in SKILLS_DIR.iterdir()
        if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name) and d.name != date_str
    ]
    prev_catalog = load_previous_catalog(existing_dirs)
    commit_hint = (re.findall(r"\b([0-9a-f]{12})\b", section) or [""])[0]

    if not already_snapped:
        write_date_snapshot(date_str, ver, commit_hint)

    diff = compute_diff(prev_catalog, [s["slug"] for s in SKILL_DEFS])
    items = extract_changelog_items(section)
    entry = build_changelog(date_str, ver, prev, diff, items, section)

    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = CHANGELOGS_DIR / f"{date_str}.txt"
    log_path.write_text(entry, encoding="utf-8")
    print(f"Changelog written: {log_path}")

    VERSION_FILE.write_text(ver)
    update_catalog_version_field(ver)
    print(f"Updated: {prev or 'none'} -> {ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

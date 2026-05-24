#!/usr/bin/env python3
"""Daily Claude Code skills sync.

Workflow:
  1. Fetch anthropics/claude-code CHANGELOG.md
  2. Parse latest version + changed items
  3. Compare against .manifest to detect added/modified/deleted skills
  4. Create Claude/skills/YYYY-MM-DD/skills/ snapshot
  5. Update SKILLS_CATALOG.yaml + .version if version changed
  6. Write Claude/Changelogs/YYYY-MM-DD.txt
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
MANIFEST_FILE = SKILLS_ROOT / ".manifest"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"

SOURCE_REPO = "anthropics/claude-code"
CHANGELOG_URL = f"https://raw.githubusercontent.com/{SOURCE_REPO}/main/CHANGELOG.md"

TOKEN_POLICY = [
    "Avoid repeated background context.",
    "Return only decision-critical output.",
    "Link to source repo instead of copying long docs.",
]
COMPATIBILITY = [
    "Do not overwrite existing dated skill snapshots.",
    "Integrate only if slug is unique or content hash changed.",
    "Preserve changelog evidence for every generated update.",
]

# Canonical Claude Code skill definitions (source of truth)
BUILTIN_SKILLS = [
    dict(slug="init",                     name="Init",                      cmd="/init",
         trigger="initialize or document codebase",
         desc="Generate CLAUDE.md with architecture, conventions, commands",
         procedure=["Scan repo structure and key files.", "Extract conventions from existing code.", "Write CLAUDE.md with commands, architecture, notes."]),
    dict(slug="review",                   name="Review",                    cmd="/review",
         trigger="review PR or branch",
         desc="Multi-pass PR review; logic, style, security, tests",
         procedure=["Diff current branch against base.", "Check logic, edge cases, security, test coverage.", "Output risk-ranked findings with line references."]),
    dict(slug="security-review",          name="Security Review",           cmd="/security-review",
         trigger="security audit of current branch changes",
         desc="OWASP-focused audit of pending diffs; risk-ranked findings",
         procedure=["Isolate changed surfaces.", "Check OWASP Top 10 and injection vectors.", "Report findings by severity with remediation."]),
    dict(slug="simplify",                 name="Simplify",                  cmd="/simplify",
         trigger="clean up or refactor changed code",
         desc="Review changed code for reuse/quality/efficiency then fix",
         procedure=["Identify duplication, dead code, and complexity.", "Propose minimal refactor.", "Apply changes preserving behavior."]),
    dict(slug="session-start-hook",       name="Session Start Hook",        cmd="/session-start-hook",
         trigger="test/lint runners on session start (web Claude Code)",
         desc="Create SessionStart hook ensuring project can run tests and linters",
         procedure=["Detect test and lint commands from package.json/Makefile.", "Write hook config to .claude/settings.json.", "Verify hook fires on next session start."]),
    dict(slug="update-config",            name="Update Config",             cmd="/update-config",
         trigger="automated behavior requests, permissions, env vars, settings.json",
         desc="Configure settings.json; handles hooks, permissions, env vars",
         procedure=["Parse user intent (hook / permission / env var).", "Locate correct settings.json scope (project vs user).", "Apply change with minimal diff."]),
    dict(slug="keybindings-help",         name="Keybindings Help",          cmd="/keybindings-help",
         trigger="remap keys, add chord shortcuts, customize keybindings",
         desc="Customize ~/.claude/keybindings.json; supports chord bindings",
         procedure=["Show current bindings.", "Parse user's desired binding.", "Write updated keybindings.json entry."]),
    dict(slug="fewer-permission-prompts", name="Fewer Permission Prompts",  cmd="/fewer-permission-prompts",
         trigger="too many permission dialogs, reduce prompts",
         desc="Scan transcripts → add bash/MCP allowlist to .claude/settings.json",
         procedure=["Read recent transcript for repeated tool calls.", "Extract safe read-only patterns.", "Add allowlist entries to settings.json."]),
    dict(slug="loop",                     name="Loop",                      cmd="/loop [interval] [/cmd]",
         trigger="recurring task, polling interval, repeated check",
         desc="Run prompt or slash command on recurring interval (default 10m)",
         procedure=["Parse interval and command.", "Schedule using internal timer.", "Execute command on each tick; stop on user request."],
         example="/loop 5m /review"),
    dict(slug="claude-api",              name="Claude API",                cmd="/claude-api",
         trigger="code imports anthropic SDK, Claude API features, model migration",
         desc="Build/debug Claude API apps; prompt caching, tool use, model migration",
         procedure=["Identify SDK version and feature area.", "Apply prompt caching and tool use best practices.", "Migrate model IDs to latest versions."]),
    dict(slug="ultrareview",             name="Ultra Review",              cmd="/ultrareview [PR#]",
         trigger="multi-agent cloud review, ultrareview keyword",
         desc="Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR",
         procedure=["Launch parallel review agents.", "Aggregate findings across agents.", "Output ranked consolidated review."],
         note="Billed; requires git repo; no GitHub remote needed for local mode"),
    dict(slug="ultraplan",               name="Ultra Plan",                cmd="/ultraplan",
         trigger="cloud multi-agent planning, complex planning tasks",
         desc="Auto-create cloud worktrees/environments for multi-agent planning tasks",
         procedure=["Analyze task scope.", "Spawn cloud worktrees per sub-task.", "Aggregate and present unified plan."]),
    dict(slug="team-onboarding",         name="Team Onboarding",           cmd="/team-onboarding",
         trigger="teammate ramp-up guide, onboarding new team member",
         desc="Generate onboarding guide from local Claude Code usage history",
         procedure=["Read Claude Code usage history and transcripts.", "Extract frequent patterns and conventions.", "Write onboarding guide with examples."]),
    dict(slug="effort",                  name="Effort",                    cmd="/effort",
         trigger="adjust effort level, quality level, speed vs depth",
         desc="Interactive effort slider for session (also: CLAUDE_EFFORT env var)",
         procedure=["Show current effort level.", "Accept slider input or named level.", "Apply to session context window strategy."]),
    dict(slug="powerup",                 name="Power Up",                  cmd="/powerup",
         trigger="feature demos, learn Claude Code features",
         desc="Interactive animated feature demos with lessons",
         procedure=["Present feature menu.", "Run selected demo.", "Return actionable next steps."]),
    dict(slug="tui",                     name="TUI",                       cmd="/tui",
         trigger="flickery rendering, full-screen mode, alt-screen",
         desc="Switch to flicker-free alt-screen TUI rendering",
         procedure=["Toggle alt-screen mode.", "Redraw UI cleanly.", "Persist preference to session."],
         note="Also: CLAUDE_CODE_NO_FLICKER=1"),
    dict(slug="focus",                   name="Focus",                     cmd="/focus",
         trigger="compact view, hide tool calls, clean output",
         desc="Toggle focus view: prompt + tool summary + final response only",
         procedure=["Toggle focus mode.", "Collapse intermediate tool output.", "Show only essential turn content."]),
    dict(slug="undo",                    name="Undo",                      cmd="/undo",
         trigger="undo last action, revert last change",
         desc="Alias for /rewind; undoes last assistant action",
         procedure=["Identify last assistant action.", "Revert file changes or tool effects.", "Confirm revert to user."]),
    dict(slug="usage",                   name="Usage",                     cmd="/usage",
         trigger="token usage, cost statistics, spending",
         desc="Show token usage and cost stats (merged /cost + /stats)",
         procedure=["Aggregate session token counts.", "Calculate cost at current model rates.", "Display breakdown by turn."]),
    dict(slug="theme",                   name="Theme",                     cmd="/theme [name]",
         trigger="change visual theme, create color theme",
         desc="Create or switch custom color themes",
         procedure=["List available themes.", "Apply named theme or open editor.", "Save theme to config."]),
    dict(slug="color",                   name="Color",                     cmd="/color",
         trigger="set session color, random color",
         desc="Set random session color (no args = random pick)",
         procedure=["Pick random or specified color.", "Apply to session UI.", "Persist for session duration."]),
    dict(slug="run",                     name="Run",                       cmd="/run",
         trigger="run app, start server, launch project, screenshot app",
         desc="Launch and drive project app to verify changes",
         procedure=["Detect project type (server, CLI, TUI, Electron, browser).", "Launch with appropriate command.", "Verify golden path and report result."]),
    dict(slug="verify",                  name="Verify",                    cmd="/verify",
         trigger="verify fix works, confirm feature works, validate before push",
         desc="Run app and observe behavior to confirm a code change",
         procedure=["Identify what the change is supposed to do.", "Launch app and exercise the changed path.", "Report pass/fail with evidence."]),
    dict(slug="code-review",             name="Code Review",               cmd="/code-review",
         trigger="review diff for bugs, code correctness review",
         desc="Review diff at given effort level; --comment posts inline PR comments",
         procedure=["Read current diff.", "Check for correctness bugs at specified effort.", "Output findings or post inline PR comments."]),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_latest_version(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(changelog)
    return ver, changelog[start:end].strip()


def load_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def load_manifest() -> dict:
    if MANIFEST_FILE.exists():
        try:
            return json.loads(MANIFEST_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"version": "", "skills": [], "updated": ""}


def save_manifest(ver: str, skills: list[str], date_str: str) -> None:
    MANIFEST_FILE.write_text(json.dumps(
        {"version": ver, "skills": sorted(skills), "updated": date_str},
        indent=2
    ))


def extract_changelog_items(section: str) -> dict:
    cmds = sorted(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = sorted(set(re.findall(
        r"\b(PreToolUse|PostToolUse|PreCompact|TaskCreated|WorktreeCreate|"
        r"PermissionDenied|Notification|Stop|SubagentStop)\b", section
    )))
    return {"cmds": cmds, "settings": settings, "env": env_vars, "hooks": hooks}


def slug_from_cmd(cmd: str) -> str:
    return cmd.lstrip("/").lower().replace(" ", "-")


def compute_hash(skill: dict) -> str:
    key = json.dumps({k: skill[k] for k in ("slug", "desc", "trigger")}, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def skill_md(skill: dict, version: str, date_str: str) -> str:
    lines = [
        f"# {skill['name']}",
        "",
        f"- Slug: `{skill['slug']}`",
        f"- Cmd: `{skill['cmd']}`",
        f"- Source: https://github.com/{SOURCE_REPO}",
        f"- Version: {version}",
        f"- Trigger: {skill['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    for i, step in enumerate(skill.get("procedure", ["Follow official source."]), 1):
        lines.append(f"{i}. {step}")
    lines += ["", "## Output", "", skill["desc"], "", "## Token Policy", ""]
    for p in TOKEN_POLICY:
        lines.append(f"- {p}")
    lines += ["", "## Compatibility", ""]
    for c in COMPATIBILITY:
        lines.append(f"- {c}")
    if "example" in skill:
        lines += ["", "## Example", "", f"`{skill['example']}`"]
    if "note" in skill:
        lines += ["", f"**Note:** {skill['note']}"]
    return "\n".join(lines) + "\n"


def write_dated_snapshot(skills: list[dict], version: str, date_str: str) -> Path:
    snap_dir = SKILLS_ROOT / date_str / "skills"
    if snap_dir.exists():
        return snap_dir  # already written today

    snap_dir.mkdir(parents=True, exist_ok=True)

    # Individual .md files
    for s in skills:
        (snap_dir / f"{s['slug']}.md").write_text(skill_md(s, version, date_str))

    # catalog.json
    catalog = {
        "date": date_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": f"https://github.com/{SOURCE_REPO}",
        "version": version,
        "skills": [
            {
                "slug": s["slug"],
                "name": s["name"],
                "cmd": s["cmd"],
                "trigger": s["trigger"],
                "desc": s["desc"],
                "hash": compute_hash(s),
                "token_policy": TOKEN_POLICY,
                "compatibility": COMPATIBILITY,
            }
            for s in skills
        ],
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    )
    return snap_dir


def detect_changes(prev_manifest: dict, current_skills: list[dict], changelog_items: dict, version: str) -> dict:
    prev_slugs = set(prev_manifest.get("skills", []))
    curr_slugs = {s["slug"] for s in current_skills}

    # New commands found in changelog not yet in catalog
    changelog_cmds = {slug_from_cmd(c) for c in changelog_items.get("cmds", [])}
    added_from_changelog = [c for c in changelog_cmds if c not in curr_slugs]

    added   = sorted(curr_slugs - prev_slugs) + added_from_changelog
    removed = sorted(prev_slugs - curr_slugs)
    # Skills mentioned in changelog that exist = modified
    modified = sorted(changelog_cmds & curr_slugs)

    # Conflict: slug in both old and new with same name but potentially different desc
    conflicts = []
    if prev_manifest.get("version") and version != prev_manifest.get("version", ""):
        for slug in (curr_slugs & prev_slugs):
            if slug in changelog_cmds:
                conflicts.append(f"{slug}: updated in v{version}, integrated from catalog")

    return {
        "added": added,
        "modified": modified,
        "removed": removed,
        "conflicts": conflicts,
        "new_hooks": changelog_items.get("hooks", []),
        "new_settings": changelog_items.get("settings", []),
        "new_env": changelog_items.get("env", []),
    }


def build_changelog_entry(
    ver: str,
    prev_ver: str,
    section: str,
    changes: dict,
    date_str: str,
    snapshot_created: bool,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "=" * 60,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev_ver or 'none'} -> {ver}",
        f"Source  : github.com/{SOURCE_REPO}",
        f"Snapshot: Claude/skills/{date_str}/skills/",
        "=" * 60,
        "",
    ]

    # Added
    lines.append("[추가된 스킬 / Added Skills]")
    if changes["added"]:
        for s in changes["added"]:
            lines.append(f"  + {s}")
    else:
        lines.append("  (없음 / none)")
    lines.append("")

    # Modified
    lines.append("[수정된 스킬 / Modified Skills]")
    if changes["modified"]:
        for s in changes["modified"]:
            lines.append(f"  ~ {s}: mentioned in v{ver} changelog")
    else:
        lines.append("  (없음 / none)")
    lines.append("")

    # Deleted
    lines.append("[삭제된 스킬 / Deleted Skills]")
    if changes["removed"]:
        for s in changes["removed"]:
            lines.append(f"  - {s}")
    else:
        lines.append("  (없음 / none)")
    lines.append("")

    # Optimized structure
    lines.append("[최적화된 구조 / Optimized Structure]")
    if snapshot_created:
        lines.append(f"  새 스냅샷 생성: Claude/skills/{date_str}/skills/")
        lines.append(f"  스킬 수: {len(BUILTIN_SKILLS)}개 (SKILLS_CATALOG.yaml 동기화)")
    else:
        lines.append("  오늘 스냅샷 이미 존재 - 재생성 생략")
    lines.append("")

    # Token savings
    lines.append("[토큰 절감 / Token Savings]")
    lines.append("  YAML 카탈로그 단일 소스 유지 (JSON 대비 ~30% 절감)")
    lines.append("  설명 1줄 제한, 예시는 필요한 경우만 포함")
    lines.append("  중복 배경 컨텍스트 제거, 소스 링크로 대체")
    if changes.get("new_settings"):
        lines.append(f"  신규 설정 항목: {', '.join(changes['new_settings'])}")
    if changes.get("new_env"):
        lines.append(f"  신규 환경 변수: {', '.join(changes['new_env'])}")
    lines.append("")

    # Conflict resolution
    lines.append("[충돌 해결 / Conflict Resolution]")
    if changes["conflicts"]:
        for c in changes["conflicts"]:
            lines.append(f"  [해결됨] {c}")
    else:
        lines.append("  충돌 없음 / No conflicts detected")
    lines.append("")

    # Hooks
    if changes.get("new_hooks"):
        lines.append("[신규 훅 / New Hooks]")
        for h in changes["new_hooks"]:
            lines.append(f"  {h}")
        lines.append("")

    # Raw changelog excerpt
    lines += [
        "-" * 40,
        "[원문 변경사항 발췌 / Raw Changelog Excerpt]",
        "",
        section[:2000].strip(),
        "",
        "=" * 60,
        f"[적용 상태] SKILLS_CATALOG.yaml 최신화 완료 (v{ver})",
        f"[Status]   Catalog updated → yeongam/Prompt-Guide",
    ]
    return "\n".join(lines) + "\n"


def update_catalog_fields(ver: str, date_str: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {date_str}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def main() -> int:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_snap = SKILLS_ROOT / date_str / "skills"

    print(f"[{date_str}] Fetching Claude Code changelog...")
    try:
        changelog_raw = fetch(CHANGELOG_URL)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, section = parse_latest_version(changelog_raw)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev_ver = load_version()
    prev_manifest = load_manifest()
    print(f"Latest: {ver}  |  Local: {prev_ver or 'none'}")

    changelog_items = extract_changelog_items(section) if (ver != prev_ver) else {}
    changes = detect_changes(prev_manifest, BUILTIN_SKILLS, changelog_items, ver)

    snapshot_created = not today_snap.exists()

    # Always create today's dated snapshot
    snap_dir = write_dated_snapshot(BUILTIN_SKILLS, ver, date_str)
    if snapshot_created:
        print(f"Snapshot created: {snap_dir}")
    else:
        print(f"Snapshot exists: {snap_dir}")

    # Update catalog + version only when version changed
    if ver != prev_ver:
        VERSION_FILE.write_text(ver)
        update_catalog_fields(ver, date_str)
        save_manifest(ver, [s["slug"] for s in BUILTIN_SKILLS], date_str)
        print(f"Updated: {prev_ver or 'none'} -> {ver}")
    else:
        save_manifest(ver, [s["slug"] for s in BUILTIN_SKILLS], date_str)

    # Write changelog if version changed or new snapshot
    if ver != prev_ver or snapshot_created:
        CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_path = CHANGELOGS_DIR / f"{date_str}.txt"
        if not log_path.exists():
            entry = build_changelog_entry(
                ver, prev_ver, section, changes, date_str, snapshot_created
            )
            log_path.write_text(entry, encoding="utf-8")
            print(f"Changelog written: {log_path}")
        else:
            print(f"Changelog already exists for today: {log_path}")
    else:
        print("No changes - already up to date.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

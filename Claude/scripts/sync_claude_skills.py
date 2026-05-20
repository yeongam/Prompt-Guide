#!/usr/bin/env python3
"""Daily Claude Code skills sync.

Fetches CHANGELOG from anthropics/claude-code, builds dated skill snapshots
under Claude/skills/YYYY-MM-DD/skills/, updates SKILLS_CATALOG.yaml,
and writes Claude/Changelogs/YYYY-MM-DD.txt.
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).parent.parent.parent   # Prompt-Guide/
CLAUDE_DIR  = REPO_ROOT / "Claude"
SKILLS_ROOT = CLAUDE_DIR / "skills"
CATALOG     = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_F   = SKILLS_ROOT / ".version"
CHANGELOGS  = CLAUDE_DIR / "Changelogs"
CHANGELOG_URL = (
    "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
)

# ── Canonical skill definitions ───────────────────────────────────────────────
SKILLS: list[dict] = [
    {
        "slug": "init", "name": "Init Codebase", "cmd": "/init",
        "trigger": "user asks to initialize or document codebase",
        "desc": "Generate CLAUDE.md with codebase architecture, conventions, commands",
        "output": "CLAUDE.md documenting project structure and conventions.",
        "procedure": [
            "Read existing code structure.",
            "Extract conventions and commands.",
            "Write concise CLAUDE.md.",
            "Verify with /review.",
        ],
        "token_policy": [
            "Skip sections with no content.",
            "One sentence per convention.",
            "Link source files, don't inline them.",
        ],
    },
    {
        "slug": "review", "name": "PR Review", "cmd": "/review",
        "trigger": "user asks to review PR or branch",
        "desc": "Multi-pass PR review; checks logic, style, security, tests",
        "output": "Ranked findings with severity and fix suggestions.",
        "procedure": [
            "Fetch diff.",
            "Check logic correctness.",
            "Check style and naming.",
            "Check security (OWASP Top 10).",
            "Check test coverage.",
        ],
        "token_policy": [
            "Return findings only, not unchanged lines.",
            "Group by severity.",
            "Link to line numbers.",
        ],
    },
    {
        "slug": "security-review", "name": "Security Review", "cmd": "/security-review",
        "trigger": "user asks security audit of current branch changes",
        "desc": "OWASP-focused audit of pending diffs; outputs risk-ranked findings",
        "output": "Risk-ranked security findings with remediation steps.",
        "procedure": [
            "Diff current branch.",
            "Map findings to OWASP Top 10.",
            "Rank by severity.",
            "Suggest minimal fixes.",
        ],
        "token_policy": [
            "Skip low-risk items unless pattern is widespread.",
            "Cite OWASP reference codes.",
        ],
    },
    {
        "slug": "simplify", "name": "Simplify Code", "cmd": "/simplify",
        "trigger": "user asks to clean up or refactor changed code",
        "desc": "Review changed code for reuse/quality/efficiency, then fix issues",
        "output": "Refactored diff with one-line rationale per change.",
        "procedure": [
            "Identify duplication.",
            "Apply DRY where safe.",
            "Remove dead code.",
            "Verify tests still pass.",
        ],
        "token_policy": [
            "Show diff only, not full file.",
            "One-line rationale per change.",
        ],
    },
    {
        "slug": "session-start-hook", "name": "Session Start Hook",
        "cmd": "/session-start-hook",
        "trigger": "user wants test/lint runners on session start (web Claude Code)",
        "desc": "Create SessionStart hook ensuring project can run tests and linters",
        "output": "SessionStart hook config in .claude/settings.json.",
        "procedure": [
            "Detect project type.",
            "Find test and lint commands.",
            "Write hook entry to settings.json.",
            "Verify hook fires on next session.",
        ],
        "token_policy": [
            "Emit only the JSON diff for settings.json.",
            "Skip explanation if command is self-evident.",
        ],
    },
    {
        "slug": "update-config", "name": "Update Config", "cmd": "/update-config",
        "trigger": "automated behavior requests (when X, allow Y, set Z=val)",
        "desc": "Configure settings.json; handles hooks, permissions, env vars",
        "output": "Updated settings.json diff.",
        "procedure": [
            "Identify target config scope (project/user).",
            "Locate or create settings.json.",
            "Apply minimal change.",
            "Confirm effect.",
        ],
        "token_policy": [
            "Emit only changed JSON keys.",
            "No full-file reprint.",
        ],
    },
    {
        "slug": "keybindings-help", "name": "Keybindings Help",
        "cmd": "/keybindings-help",
        "trigger": "user wants to remap keys or add chord shortcuts",
        "desc": "Customize ~/.claude/keybindings.json; supports chord bindings",
        "output": "Keybinding JSON entries to add or modify.",
        "procedure": [
            "Read current keybindings.json.",
            "Identify conflicts.",
            "Add or update bindings.",
            "List new shortcuts.",
        ],
        "token_policy": [
            "Emit new/changed entries only.",
            "Skip unchanged bindings.",
        ],
    },
    {
        "slug": "fewer-permission-prompts", "name": "Fewer Permission Prompts",
        "cmd": "/fewer-permission-prompts",
        "trigger": "user wants fewer permission dialogs",
        "desc": "Scan transcripts -> add bash/MCP allowlist to .claude/settings.json",
        "output": "Updated allowlist in .claude/settings.json.",
        "procedure": [
            "Scan recent transcripts for denied commands.",
            "Group by tool type.",
            "Add to allowlist.",
            "Verify no over-permissioning.",
        ],
        "token_policy": [
            "List allowed patterns only.",
            "Group by tool category.",
        ],
    },
    {
        "slug": "loop", "name": "Loop Task", "cmd": "/loop [interval] [/command]",
        "trigger": "user wants recurring task (e.g. check every 5m, keep running X)",
        "desc": "Run prompt or slash command on recurring interval (default 10m)",
        "output": "Recurring task registered with interval.",
        "procedure": [
            "Parse interval (default 10m).",
            "Register loop.",
            "Execute command on each tick.",
            "Stop on /stop or user request.",
        ],
        "token_policy": [
            "Log tick count, not full output each time.",
            "Summarize across ticks on stop.",
        ],
        "example": "/loop 5m /review",
    },
    {
        "slug": "claude-api", "name": "Claude API", "cmd": "/claude-api",
        "trigger": "code imports anthropic SDK; user asks about Claude API features",
        "desc": "Build/debug Claude API apps; prompt caching, tool use, model migration",
        "output": "Working API code with caching and correct model IDs.",
        "procedure": [
            "Identify SDK usage pattern.",
            "Apply prompt caching where applicable.",
            "Use correct model ID.",
            "Verify tool use schema.",
        ],
        "token_policy": [
            "Show only changed code blocks.",
            "Reference SDK docs by URL, not inline copy.",
        ],
        "models": {
            "opus": "claude-opus-4-7",
            "sonnet": "claude-sonnet-4-6",
            "haiku": "claude-haiku-4-5-20251001",
        },
    },
    {
        "slug": "ultrareview", "name": "UltraReview", "cmd": "/ultrareview [PR#]",
        "trigger": "user says ultrareview or wants multi-agent review",
        "desc": "Parallel multi-agent cloud review; no-arg=local branch, arg=GitHub PR",
        "output": "Multi-agent review report with parallel findings merged.",
        "procedure": [
            "Determine target (local branch or PR#).",
            "Spawn parallel review agents.",
            "Merge findings.",
            "Return ranked report.",
        ],
        "token_policy": [
            "Return merged report only, not per-agent transcripts.",
            "Billed; note cost estimate before starting.",
        ],
    },
    {
        "slug": "ultraplan", "name": "UltraPlan", "cmd": "/ultraplan",
        "trigger": "user wants cloud environment for complex planning",
        "desc": "Auto-create cloud worktrees/environments for multi-agent planning tasks",
        "output": "Planning environment created with task breakdown.",
        "procedure": [
            "Parse task scope.",
            "Create cloud worktrees.",
            "Assign subtasks to agents.",
            "Synthesize plan.",
        ],
        "token_policy": [
            "Return final plan only.",
            "Omit agent coordination logs.",
        ],
    },
    {
        "slug": "team-onboarding", "name": "Team Onboarding",
        "cmd": "/team-onboarding",
        "trigger": "user wants teammate ramp-up guide",
        "desc": "Generate onboarding guide from local Claude Code usage history/data",
        "output": "Onboarding guide markdown with project-specific tips.",
        "procedure": [
            "Read CLAUDE.md and usage history.",
            "Identify common tasks.",
            "Write step-by-step guide.",
            "Include key commands.",
        ],
        "token_policy": [
            "One sentence per tip.",
            "Skip generic advice already in README.",
        ],
    },
    {
        "slug": "effort", "name": "Effort Level", "cmd": "/effort",
        "trigger": "user wants to adjust effort/quality level",
        "desc": "Interactive slider for session effort level (also: CLAUDE_EFFORT env var)",
        "output": "Effort level confirmed; CLAUDE_EFFORT set.",
        "procedure": [
            "Show current level.",
            "Accept new level (1-5).",
            "Set CLAUDE_EFFORT.",
            "Confirm effect on response depth.",
        ],
        "token_policy": [
            "Emit only level change confirmation.",
            "No explanation of levels unless asked.",
        ],
    },
    {
        "slug": "powerup", "name": "Powerup Demos", "cmd": "/powerup",
        "trigger": "user wants feature demos or to learn Claude Code features",
        "desc": "Interactive animated feature demos with lessons",
        "output": "Demo sequence for selected feature.",
        "procedure": [
            "List available demos.",
            "Run selected demo.",
            "Pause for user confirmation between steps.",
        ],
        "token_policy": [
            "One feature per demo run.",
            "Skip already-seen demos if history available.",
        ],
    },
    {
        "slug": "tui", "name": "TUI Mode", "cmd": "/tui",
        "trigger": "rendering looks flickery or user wants full-screen mode",
        "desc": "Switch to flicker-free alt-screen TUI rendering",
        "output": "TUI mode activated.",
        "procedure": [
            "Toggle CLAUDE_CODE_NO_FLICKER.",
            "Restart rendering context.",
            "Confirm flicker-free state.",
        ],
        "token_policy": ["Confirmation only; no setup narrative."],
    },
    {
        "slug": "focus", "name": "Focus View", "cmd": "/focus",
        "trigger": "user wants compact view of conversation",
        "desc": "Toggle focus view: prompt + tool summary + final response only",
        "output": "Focus view toggled.",
        "procedure": ["Toggle focus mode.", "Confirm current state."],
        "token_policy": ["One-line confirmation."],
    },
    {
        "slug": "undo", "name": "Undo Action", "cmd": "/undo",
        "trigger": "user wants to undo last action",
        "desc": "Alias for /rewind; undoes last assistant action",
        "output": "Last action undone.",
        "procedure": ["Identify last action.", "Revert it.", "Confirm state."],
        "token_policy": ["One-line confirmation."],
    },
    {
        "slug": "usage", "name": "Usage Stats", "cmd": "/usage",
        "trigger": "user asks about token or cost statistics",
        "desc": "Show token usage and cost stats (merged /cost + /stats)",
        "output": "Token and cost summary for current session.",
        "procedure": [
            "Aggregate token counts.",
            "Calculate cost by model.",
            "Show breakdown table.",
        ],
        "token_policy": ["Table format; no narrative."],
    },
    {
        "slug": "theme", "name": "Theme", "cmd": "/theme [name]",
        "trigger": "user wants to change or create visual theme",
        "desc": "Create or switch custom color themes",
        "output": "Theme applied or created.",
        "procedure": [
            "List available themes.",
            "Apply or create requested theme.",
            "Confirm change.",
        ],
        "token_policy": ["Color hex values only; no design narrative."],
    },
    {
        "slug": "color", "name": "Session Color", "cmd": "/color",
        "trigger": "user wants a session color",
        "desc": "Set random session color (no args = random pick)",
        "output": "Session color set.",
        "procedure": [
            "Pick random color if no arg.",
            "Apply to session.",
            "Show hex value.",
        ],
        "token_policy": ["One-line: color name + hex."],
    },
    {
        "slug": "verify", "name": "Verify Change", "cmd": "/verify",
        "trigger": "user asks to verify a change works, confirm a fix, or test manually",
        "desc": "Run app and observe behavior to confirm change works end-to-end",
        "output": "Pass/fail result with observed behavior summary.",
        "procedure": [
            "Identify golden path to test.",
            "Run app or relevant command.",
            "Observe output against expectation.",
            "Report edge case regressions if found.",
        ],
        "token_policy": [
            "Report result + one-line evidence only.",
            "Skip steps that succeeded without incident.",
        ],
    },
    {
        "slug": "run", "name": "Run App", "cmd": "/run",
        "trigger": "user asks to run, start, or screenshot the app",
        "desc": "Launch project app and confirm change works in live environment",
        "output": "App running confirmation with startup log snippet.",
        "procedure": [
            "Detect project type (CLI/server/TUI/browser).",
            "Find launch command.",
            "Start app.",
            "Report ready state or errors.",
        ],
        "token_policy": [
            "Show startup log tail only.",
            "Skip healthy check output.",
        ],
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-sync/2.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def skill_hash(s: dict) -> str:
    key = json.dumps({k: s[k] for k in sorted(s) if k != "hash"}, sort_keys=True)
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def parse_changelog(text: str) -> tuple[str, str]:
    """Return (latest_version, section_text) from CHANGELOG.md."""
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", text)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", text[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(text)
    return ver, text[start:end].strip()


def current_version() -> str:
    return VERSION_F.read_text().strip() if VERSION_F.exists() else ""


def latest_snapshot_dir() -> Path | None:
    """Return the most recent dated snapshot dir under Claude/skills/, or None."""
    dirs = sorted(
        (d for d in SKILLS_ROOT.iterdir()
         if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name)),
        key=lambda d: d.name,
    )
    return dirs[-1] if dirs else None


def load_snapshot_catalog(snap_dir: Path | None) -> dict[str, dict]:
    """Return slug -> skill dict from snapshot catalog.json, or {}."""
    if snap_dir is None:
        return {}
    cat_file = snap_dir / "skills" / "catalog.json"
    if not cat_file.exists():
        return {}
    data = json.loads(cat_file.read_text())
    return {s["slug"]: s for s in data.get("skills", [])}


def extract_upstream_items(section: str) -> dict:
    """Extract skill/hook/setting mentions from a CHANGELOG section."""
    return {
        "skills":   sorted(set(re.findall(r"`(/[\w-]+)`", section))),
        "settings": sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section))),
        "env":      sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section))),
        "hooks":    sorted(set(re.findall(
            r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|"
            r"Notification|Stop|SubagentStop)\b", section))),
    }


# ── Snapshot writers ──────────────────────────────────────────────────────────

def write_skill_md(skill_dir: Path, s: dict, ver: str) -> None:
    lines = [
        f"# {s['name']}",
        "",
        f"- Slug: `{s['slug']}`",
        f"- Cmd: `{s['cmd']}`",
        f"- Source: anthropics/claude-code v{ver}",
        f"- Trigger: {s['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    lines += [f"{i+1}. {step}" for i, step in enumerate(s["procedure"])]
    lines += ["", "## Output", "", s["output"], "", "## Token Policy", ""]
    lines += [f"- {p}" for p in s["token_policy"]]
    if "example" in s:
        lines += ["", "## Example", "", f"`{s['example']}`"]
    if "models" in s:
        lines += ["", "## Models", ""]
        lines += [f"- {k}: `{v}`" for k, v in s["models"].items()]
    lines += [
        "", "## Compatibility", "",
        "- Do not overwrite existing dated skill snapshots.",
        "- Integrate only if slug is unique or content hash changed.",
        "- Preserve changelog evidence for every generated update.",
    ]
    (skill_dir / f"{s['slug']}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_snapshot(date_str: str, ver: str) -> None:
    snap_dir = SKILLS_ROOT / date_str / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)

    now_iso = datetime.now(timezone.utc).isoformat()
    catalog_skills = []
    for s in SKILLS:
        h = skill_hash(s)
        entry = {
            "slug": s["slug"],
            "name": s["name"],
            "cmd": s["cmd"],
            "trigger": s["trigger"],
            "desc": s["desc"],
            "output": s["output"],
            "procedure": s["procedure"],
            "token_policy": s["token_policy"],
            "hash": h,
            "source": "anthropics/claude-code",
            "source_version": ver,
            "compatibility": [
                "Do not overwrite existing dated skill snapshots.",
                "Integrate only if slug is unique or content hash changed.",
                "Preserve changelog evidence for every generated update.",
            ],
        }
        if "models" in s:
            entry["models"] = s["models"]
        if "example" in s:
            entry["example"] = s["example"]
        catalog_skills.append(entry)
        write_skill_md(snap_dir, s, ver)

    catalog = {
        "date": date_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "generated_at": now_iso,
        "source": "anthropics/claude-code",
        "source_url": "https://github.com/anthropics/claude-code",
        "version": ver,
        "skills": catalog_skills,
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Snapshot written: {snap_dir} ({len(SKILLS)} skills)")


# ── Changelog writer ──────────────────────────────────────────────────────────

def diff_skills(prev: dict[str, dict], curr_skills: list[dict]) -> tuple[list, list, list]:
    curr = {s["slug"]: s for s in curr_skills}
    added    = [s for slug, s in curr.items() if slug not in prev]
    deleted  = [s for slug, s in prev.items() if slug not in curr]
    modified = [
        curr[slug] for slug in curr
        if slug in prev and skill_hash(curr[slug]) != prev[slug].get("hash", "")
    ]
    return added, modified, deleted


def write_changelog(
    date_str: str, ver: str, prev_ver: str,
    added: list, modified: list, deleted: list,
    upstream_items: dict, section_raw: str,
) -> None:
    CHANGELOGS.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def bullet(items: list) -> list[str]:
        return [f"  - {s['name']} ({s['slug']})" for s in items] if items else ["  - (없음)"]

    def upstream_block(label: str, items: list) -> list[str]:
        return ([f"  {label}:"] + [f"    {x}" for x in items]) if items else []

    token_savings = []
    if added or modified:
        token_savings.append("  - 불필요한 설명 제거; 각 스킬 desc 1줄 제한 유지")
        token_savings.append("  - procedure/token_policy 리스트 항목 최소화")
        token_savings.append("  - catalog.json에 source_version 필드 추가로 중복 URL 제거")
    if not token_savings:
        token_savings = ["  - 변경 없음; 기존 최적화 구조 유지"]

    conflict_notes: list[str] = []
    if modified:
        for s in modified:
            conflict_notes.append(f"  - {s['slug']}: 콘텐츠 해시 변경 감지 -> 새 스냅샷으로 통합")
    if not conflict_notes:
        conflict_notes = ["  - 충돌 없음"]

    lines = [
        "=" * 60,
        "Claude Code Skills 변경 로그 / Change Report",
        f"날짜    : {now}",
        f"버전    : {prev_ver or 'none'} -> {ver}",
        f"소스    : anthropics/claude-code",
        f"스냅샷  : Claude/skills/{date_str}/skills/",
        "=" * 60,
        "",
        "[추가된 스킬]",
        *bullet(added),
        "",
        "[수정된 스킬]",
        *bullet(modified),
        "",
        "[삭제된 스킬]",
        *bullet(deleted),
        "",
        "[최적화된 구조]",
        "  - 날짜/skills 디렉토리 규칙 준수 (YYYY-MM-DD/skills/)",
        "  - SKILLS_CATALOG.yaml 단일 정규 소스 유지",
        "  - 각 스킬: {slug}.md + catalog.json 이중 구조",
        "",
        "[토큰 절감 관련 변경 사항]",
        *token_savings,
        "",
        "[충돌 해결 내역]",
        *conflict_notes,
        "",
    ]

    if upstream_items["skills"] or upstream_items["hooks"] or upstream_items["settings"]:
        lines += ["-" * 40, "[업스트림 변경 감지 / Upstream Changes Detected]", ""]
        lines += upstream_block("Commands/Skills", upstream_items["skills"])
        lines += upstream_block("Hooks", upstream_items["hooks"])
        lines += upstream_block("Settings", upstream_items["settings"])
        lines += upstream_block("Env Vars", upstream_items["env"])
        lines += [
            "",
            "[원문 (발췌) / Raw Section (excerpt)]",
            "",
            section_raw[:2000],
            "",
        ]

    lines += [
        "=" * 60,
        "[상태] SKILLS_CATALOG.yaml 최신화 완료",
        f"[Status] Snapshot committed to yeongam/Prompt-Guide",
    ]

    out = CHANGELOGS / f"{date_str}.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Changelog written: {out}")


# ── Catalog updater ───────────────────────────────────────────────────────────

def update_catalog(ver: str, date_str: str) -> None:
    if not CATALOG.exists():
        return
    text = CATALOG.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {date_str}", text, flags=re.MULTILINE)
    CATALOG.write_text(text)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        raw = fetch(CHANGELOG_URL)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, section = parse_changelog(raw)
    if not ver:
        print("Could not parse version from CHANGELOG.", file=sys.stderr)
        return 1

    prev_ver   = current_version()
    date_str   = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prev_snap  = latest_snapshot_dir()
    prev_catalog = load_snapshot_catalog(prev_snap)

    print(f"Upstream: {ver}  |  Local: {prev_ver or 'none'}")
    print(f"Previous snapshot: {prev_snap.name if prev_snap else 'none'}")

    # Always create today's snapshot (idempotent if re-run same day)
    snap_today = SKILLS_ROOT / date_str / "skills"
    if snap_today.exists() and ver == prev_ver:
        print("Already up to date and today's snapshot exists. Nothing to do.")
        return 0

    added, modified, deleted = diff_skills(prev_catalog, SKILLS)
    upstream_items = extract_upstream_items(section) if ver != prev_ver else {
        "skills": [], "hooks": [], "settings": [], "env": [],
    }

    write_snapshot(date_str, ver)
    write_changelog(date_str, ver, prev_ver, added, modified, deleted,
                    upstream_items, section)
    VERSION_F.write_text(ver + "\n")
    update_catalog(ver, date_str)

    print(f"Done. {len(added)} added, {len(modified)} modified, {len(deleted)} deleted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

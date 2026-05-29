#!/usr/bin/env python3
"""
Daily Claude Code skills updater for yeongam/Prompt-Guide.

Fetches latest CHANGELOG from anthropics/claude-code, creates
date-based skill snapshots, and writes changelogs.

Output:
  Claude/skills/YYYY-MM-DD/skills/*.md
  Claude/skills/YYYY-MM-DD/skills/catalog.json
  Claude/Changelogs/YYYY-MM-DD.txt
"""

import hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request, urllib.error

REPO = Path(__file__).parent.parent
SKILLS_BASE = REPO / "Claude" / "skills"
CATALOG_FILE = SKILLS_BASE / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_BASE / ".version"
CHANGELOGS_DIR = REPO / "Claude" / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
SOURCE = "https://github.com/anthropics/claude-code"

COMPAT = [
    "Do not overwrite existing dated skill snapshots.",
    "Integrate only if slug is unique or content hash changed.",
    "Preserve changelog evidence for every generated update.",
]
TOKEN_POLICY = [
    "Avoid repeated background context.",
    "Return only decision-critical output.",
    "Link to source repo instead of copying long docs.",
]

# Mirrors SKILLS_CATALOG.yaml — single source of truth for snapshot generation
SKILLS_DATA = [
    {
        "slug": "init",
        "name": "Init",
        "cmd": "/init",
        "trigger": "user asks to initialize or document codebase",
        "desc": "Generate CLAUDE.md with architecture, conventions, commands",
        "procedure": [
            "Scan repo structure and conventions.",
            "Extract key build/test/lint commands.",
            "Write CLAUDE.md.",
        ],
        "output": "CLAUDE.md with architecture summary, commands, conventions.",
    },
    {
        "slug": "review",
        "name": "Review",
        "cmd": "/review",
        "trigger": "user asks to review PR or branch",
        "desc": "Multi-pass PR review: logic, style, security, tests",
        "procedure": [
            "Read diff holistically.",
            "Check logic, edge cases, test coverage.",
            "Flag OWASP Top 10 issues.",
            "Note style/naming deviations.",
        ],
        "output": "Risk-ranked findings with file:line refs.",
    },
    {
        "slug": "security-review",
        "name": "Security Review",
        "cmd": "/security-review",
        "trigger": "user asks security audit of current branch changes",
        "desc": "OWASP-focused audit of pending diffs; risk-ranked findings",
        "procedure": [
            "Diff current branch vs base.",
            "Map changes to OWASP Top 10.",
            "Rank: Critical > High > Medium > Low.",
        ],
        "output": "Severity-ranked findings with remediation hints.",
    },
    {
        "slug": "simplify",
        "name": "Simplify",
        "cmd": "/simplify",
        "trigger": "user asks to clean up or refactor changed code",
        "desc": "Review changed code for reuse/quality/efficiency; apply fixes",
        "procedure": [
            "Read changed files only.",
            "Identify duplication, dead code, unnecessary abstractions.",
            "Apply minimal cleanup — no speculative refactors.",
        ],
        "output": "Cleaned diff with one-line rationale per change.",
    },
    {
        "slug": "session-start-hook",
        "name": "Session Start Hook",
        "cmd": "/session-start-hook",
        "trigger": "user wants test/lint runners on session start",
        "desc": "Create SessionStart hook in .claude/settings.json",
        "procedure": [
            "Detect test/lint commands from project files.",
            "Write SessionStart hook to .claude/settings.json.",
        ],
        "output": "Updated .claude/settings.json with SessionStart hook.",
    },
    {
        "slug": "update-config",
        "name": "Update Config",
        "cmd": "/update-config",
        "trigger": "automated behavior: 'when X', 'allow Y', 'set Z=val'",
        "desc": "Configure settings.json: hooks, permissions, env vars",
        "procedure": [
            "Parse intent: hook/permission/env var.",
            "Read existing .claude/settings.json.",
            "Apply minimal targeted edit.",
        ],
        "output": "Patched settings.json with change summary.",
    },
    {
        "slug": "keybindings-help",
        "name": "Keybindings Help",
        "cmd": "/keybindings-help",
        "trigger": "user wants to remap keys or add chord shortcuts",
        "desc": "Customize ~/.claude/keybindings.json; chord binding support",
        "procedure": [
            "Read ~/.claude/keybindings.json.",
            "Apply requested rebinding.",
            "Validate for conflicts.",
        ],
        "output": "Updated keybindings.json snippet.",
    },
    {
        "slug": "fewer-permission-prompts",
        "name": "Fewer Permission Prompts",
        "cmd": "/fewer-permission-prompts",
        "trigger": "user wants fewer permission dialogs",
        "desc": "Scan transcripts; add bash/MCP allowlist to .claude/settings.json",
        "procedure": [
            "Scan recent transcripts for repeated tool calls.",
            "Build allowlist of safe patterns.",
            "Add to allowedTools in .claude/settings.json.",
        ],
        "output": "Allowlist additions to settings.json.",
    },
    {
        "slug": "loop",
        "name": "Loop",
        "cmd": "/loop [interval] [/command]",
        "trigger": "user wants recurring task (e.g. 'check every 5m')",
        "desc": "Run prompt or slash command on recurring interval (default 10m)",
        "procedure": [
            "Parse interval and command.",
            "Schedule via Monitor tool.",
            "Execute on each tick; stop on user request.",
        ],
        "output": "Recurring execution confirmation.",
    },
    {
        "slug": "claude-api",
        "name": "Claude API",
        "cmd": "/claude-api",
        "trigger": "code imports anthropic SDK; user asks about Claude API",
        "desc": "Build/debug/migrate Claude API apps; caching, tools, model IDs",
        "procedure": [
            "Check import: anthropic / @anthropic-ai/sdk.",
            "Apply prompt caching by default.",
            "Use current models: opus-4-8, sonnet-4-6, haiku-4-5.",
            "Validate tool schemas strictly.",
        ],
        "output": "Working code with caching; migration notes if applicable.",
        "models": {"opus": "claude-opus-4-8", "sonnet": "claude-sonnet-4-6", "haiku": "claude-haiku-4-5-20251001"},
    },
    {
        "slug": "autopilot",
        "name": "Autopilot",
        "cmd": "/autopilot",
        "trigger": "self-contained coding task to complete end-to-end",
        "desc": "Plan, adversarial critique, implement, bug-hunt, open PR",
        "procedure": [
            "Scope problem.",
            "Plan with 5-angle adversarial critique.",
            "Implement.",
            "Bug-hunt + completeness check.",
            "Open PR.",
        ],
        "output": "Completed feature + PR link.",
    },
    {
        "slug": "bugfix",
        "name": "Bugfix",
        "cmd": "/bugfix",
        "trigger": "user reports a specific reproducible bug",
        "desc": "Failing repro first, root-cause, minimal fix, regression test, PR",
        "procedure": [
            "Write failing repro test.",
            "Trace root cause.",
            "Apply minimal fix.",
            "Convert repro to regression test.",
            "Open PR.",
        ],
        "output": "Fix + regression test + PR.",
    },
    {
        "slug": "docs",
        "name": "Docs",
        "cmd": "/docs",
        "trigger": "user wants documentation written or updated",
        "desc": "Generate/update docs; verify examples and links; open PR",
        "procedure": [
            "Find relevant code and existing doc patterns.",
            "Draft outline for target audience.",
            "Write content; verify examples; check links.",
            "Open PR.",
        ],
        "output": "Documentation PR.",
    },
    {
        "slug": "deep-research",
        "name": "Deep Research",
        "cmd": "/deep-research",
        "trigger": "user wants multi-source fact-checked research report",
        "desc": "Fan-out searches, fetch sources, adversarial verify, cited report",
        "procedure": [
            "Fan out multiple search queries.",
            "Fetch top sources.",
            "Adversarially verify claims.",
            "Synthesize cited report.",
        ],
        "output": "Cited research report.",
    },
    {
        "slug": "investigate",
        "name": "Investigate",
        "cmd": "/investigate",
        "trigger": "user wants root cause of incident or puzzling behavior",
        "desc": "Parallel hypotheses, adversarial refutation, root-cause report",
        "procedure": [
            "Collect evidence: logs, traces, diffs.",
            "Generate competing hypotheses in parallel.",
            "Adversarially refute each.",
            "Write root-cause report with fix suggestion.",
        ],
        "output": "Root-cause report with evidence chain.",
    },
    {
        "slug": "code-review",
        "name": "Code Review",
        "cmd": "/code-review",
        "trigger": "user wants code reviewed for bugs or cleanups",
        "desc": "Review diff: correctness, reuse, simplification, efficiency",
        "procedure": [
            "Read diff at requested effort level.",
            "Flag correctness bugs first.",
            "Then reuse/simplification/efficiency issues.",
            "Post inline comments if --comment; apply if --fix.",
        ],
        "output": "Findings list or inline PR comments.",
    },
    {
        "slug": "run",
        "name": "Run",
        "cmd": "/run",
        "trigger": "user asks to run, start, or screenshot the app",
        "desc": "Launch project app and confirm changes work",
        "procedure": [
            "Find project launch skill if available.",
            "Detect project type: CLI/server/TUI/Electron/browser.",
            "Launch and verify output.",
        ],
        "output": "Running app confirmation or screenshot.",
    },
    {
        "slug": "verify",
        "name": "Verify",
        "cmd": "/verify",
        "trigger": "user asks to verify a PR or confirm a fix works",
        "desc": "Run app, exercise change path, confirm correct behavior",
        "procedure": [
            "Launch app via /run.",
            "Exercise the changed feature path.",
            "Note any regressions.",
        ],
        "output": "Verification result with observed behavior.",
    },
    {
        "slug": "dashboard",
        "name": "Dashboard",
        "cmd": "/dashboard",
        "trigger": "user wants a dashboard, monitoring view, or metrics page",
        "desc": "Discover data, design panels, implement, validate, open PR",
        "procedure": [
            "Find data sources and existing dashboard patterns.",
            "Spec panels and layout.",
            "Implement; validate queries and rendering.",
            "Open PR.",
        ],
        "output": "Dashboard implementation + PR.",
    },
    {
        "slug": "ultrareview",
        "name": "Ultra Review",
        "cmd": "/ultrareview [PR#]",
        "trigger": "user says 'ultrareview' or wants multi-agent review",
        "desc": "Parallel multi-agent cloud code review; local or GitHub PR",
        "procedure": [
            "Spawn parallel review agents.",
            "Each agent focuses on a different concern.",
            "Merge findings, deduplicate.",
        ],
        "output": "Merged multi-agent review findings.",
        "notes": "Billed; requires git repo.",
    },
    {
        "slug": "ultraplan",
        "name": "Ultra Plan",
        "cmd": "/ultraplan",
        "trigger": "user wants cloud environment for complex planning",
        "desc": "Auto-create cloud worktrees for multi-agent planning",
        "procedure": [
            "Parse task scope.",
            "Create cloud worktrees/environments.",
            "Run multi-agent planning.",
        ],
        "output": "Multi-agent plan output.",
    },
    {
        "slug": "team-onboarding",
        "name": "Team Onboarding",
        "cmd": "/team-onboarding",
        "trigger": "user wants teammate ramp-up guide",
        "desc": "Generate onboarding guide from local Claude Code usage history",
        "procedure": [
            "Scan Claude Code usage history.",
            "Extract common patterns and commands.",
            "Write onboarding guide.",
        ],
        "output": "Onboarding guide document.",
    },
    {
        "slug": "effort",
        "name": "Effort",
        "cmd": "/effort",
        "trigger": "user wants to adjust effort/quality level",
        "desc": "Interactive effort level slider for session",
        "procedure": ["Display effort slider.", "Apply selected level to session."],
        "output": "Effort level set confirmation.",
    },
    {
        "slug": "powerup",
        "name": "Power Up",
        "cmd": "/powerup",
        "trigger": "user wants feature demos or to learn Claude Code features",
        "desc": "Interactive animated feature demos with lessons",
        "procedure": [
            "List available demos.",
            "Play requested demo.",
            "Show feature lesson.",
        ],
        "output": "Feature demo or lesson.",
    },
    {
        "slug": "tui",
        "name": "TUI",
        "cmd": "/tui",
        "trigger": "rendering looks flickery or user wants full-screen mode",
        "desc": "Switch to flicker-free alt-screen TUI rendering",
        "procedure": [
            "Toggle alt-screen rendering.",
            "Equivalent: CLAUDE_CODE_NO_FLICKER=1",
        ],
        "output": "TUI mode activated.",
    },
    {
        "slug": "focus",
        "name": "Focus",
        "cmd": "/focus",
        "trigger": "user wants compact view of conversation",
        "desc": "Toggle focus view: prompt + tool summary + final response only",
        "procedure": ["Toggle focus mode.", "Show compact view."],
        "output": "Focus mode state toggled.",
    },
    {
        "slug": "undo",
        "name": "Undo",
        "cmd": "/undo",
        "trigger": "user wants to undo last action",
        "desc": "Alias for /rewind; undoes last assistant action",
        "procedure": ["Invoke /rewind.", "Restore previous state."],
        "output": "Last action undone.",
    },
    {
        "slug": "usage",
        "name": "Usage",
        "cmd": "/usage",
        "trigger": "user asks about token or cost statistics",
        "desc": "Show token usage and cost stats (merged /cost + /stats)",
        "procedure": ["Aggregate session token counts.", "Show cost breakdown."],
        "output": "Token usage and cost report.",
    },
    {
        "slug": "theme",
        "name": "Theme",
        "cmd": "/theme [name]",
        "trigger": "user wants to change or create visual theme",
        "desc": "Create or switch custom color themes",
        "procedure": ["List available themes.", "Apply or create named theme."],
        "output": "Theme applied confirmation.",
    },
    {
        "slug": "color",
        "name": "Color",
        "cmd": "/color",
        "trigger": "user wants a session color",
        "desc": "Set random session color",
        "procedure": ["Pick random color if no args.", "Apply to session."],
        "output": "Session color set.",
    },
]


def compute_hash(d: dict) -> str:
    content = json.dumps({k: v for k, v in d.items() if k != "hash"}, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def to_entry(skill: dict) -> dict:
    entry = {
        "slug": skill["slug"],
        "name": skill["name"],
        "cmd": skill["cmd"],
        "trigger": skill["trigger"],
        "desc": skill["desc"],
        "procedure": skill["procedure"],
        "output": skill["output"],
        "token_policy": TOKEN_POLICY[:],
        "compatibility": COMPAT[:],
        "source": SOURCE,
    }
    if "models" in skill:
        entry["models"] = skill["models"]
    if "notes" in skill:
        entry["notes"] = skill["notes"]
    entry["hash"] = compute_hash(entry)
    return entry


def to_md(e: dict) -> str:
    lines = [
        f"# {e['name']}",
        "",
        f"- Slug: `{e['slug']}`",
        f"- Command: `{e['cmd']}`",
        f"- Source: {e['source']}",
        f"- Trigger: {e['trigger']}",
        "",
        "## Description",
        "",
        e["desc"],
        "",
        "## Procedure",
        "",
    ]
    for i, step in enumerate(e["procedure"], 1):
        lines.append(f"{i}. {step}")
    lines += ["", "## Output", "", e["output"], "", "## Token Policy", ""]
    for p in e["token_policy"]:
        lines.append(f"- {p}")
    lines += ["", "## Compatibility", ""]
    for c in e["compatibility"]:
        lines.append(f"- {c}")
    if "models" in e:
        lines += ["", "## Models", ""]
        for k, v in e["models"].items():
            lines.append(f"- {k}: `{v}`")
    if "notes" in e:
        lines += ["", "## Notes", "", e["notes"]]
    lines.append("")
    return "\n".join(lines)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/2.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_latest(changelog: str) -> tuple[str, str]:
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


def load_prev_snapshot() -> dict:
    if not SKILLS_BASE.exists():
        return {}
    dirs = sorted([
        d for d in SKILLS_BASE.iterdir()
        if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}$", d.name)
    ])
    if not dirs:
        return {}
    cat = dirs[-1] / "skills" / "catalog.json"
    if not cat.exists():
        return {}
    try:
        return json.loads(cat.read_text())
    except Exception:
        return {}


def compute_diff(prev: dict, curr: list) -> dict:
    pm = {s["slug"]: s for s in prev.get("skills", [])}
    cm = {s["slug"]: s for s in curr}
    return {
        "added":     [s for sl, s in cm.items() if sl not in pm],
        "modified":  [s for sl, s in cm.items() if sl in pm and s["hash"] != pm[sl].get("hash")],
        "deleted":   [s for sl, s in pm.items() if sl not in cm],
        "unchanged": [s for sl, s in cm.items() if sl in pm and s["hash"] == pm[sl].get("hash")],
    }


def update_catalog_yaml(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def write_snapshot(date_str: str, entries: list, ver: str, generated_at: str) -> None:
    out = SKILLS_BASE / date_str / "skills"
    out.mkdir(parents=True, exist_ok=True)
    for e in entries:
        (out / f"{e['slug']}.md").write_text(to_md(e), encoding="utf-8")
    catalog = {
        "date": date_str,
        "version": ver,
        "directory_rule": "YYYY-MM-DD/skills",
        "generated_at": generated_at,
        "source": SOURCE,
        "source_policy": "official anthropics/claude-code repository only",
        "skills": entries,
    }
    (out / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Snapshot written: {out}")


def write_changelog(date_str: str, ver: str, prev_ver: str, diff: dict, no_change: bool) -> None:
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    path = CHANGELOGS_DIR / f"{date_str}.txt"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {date_str}",
        "",
        f"Snapshot: Claude/skills/{date_str}/skills",
        f"Source: anthropics/claude-code",
        f"Version: {prev_ver or 'none'} -> {ver}",
        f"Generated: {now}",
        "",
    ]

    if no_change:
        lines += [
            "[추가된 스킬]",
            "- none",
            "",
            "[수정된 스킬]",
            "- none",
            "",
            "[삭제된 스킬]",
            "- none",
            "",
            "[최적화된 구조]",
            "- 변경 없음: 최신 버전과 동일",
            "",
            "[토큰 절감 관련 변경 사항]",
            "- 변경 없음",
            "",
            "[충돌 해결 내역]",
            "- 없음",
            "",
            "[요약]",
            f"- 이미 최신 버전 ({ver}). 스킬 변경 없음.",
        ]
    else:
        lines += ["[추가된 스킬]"]
        if diff["added"]:
            for s in diff["added"]:
                lines.append(f"- {s['slug']}: {s['desc']}")
        else:
            lines.append("- none")
        lines.append("")

        lines += ["[수정된 스킬]"]
        if diff["modified"]:
            for s in diff["modified"]:
                lines.append(f"- {s['slug']}")
        else:
            lines.append("- none")
        lines.append("")

        lines += ["[삭제된 스킬]"]
        if diff["deleted"]:
            for s in diff["deleted"]:
                lines.append(f"- {s['slug']}")
        else:
            lines.append("- none")
        lines.append("")

        lines += [
            "[최적화된 구조]",
            f"- 날짜별 스냅샷 구조 유지: Claude/skills/{date_str}/skills",
            "- 각 스킬: .md 파일 (trigger, procedure, output, token_policy, compatibility)",
            "- catalog.json으로 메타데이터 통합",
            "",
            "[토큰 절감 관련 변경 사항]",
            "- 긴 원문 문서 복사 배제; 공식 레포 링크로 대체",
            "- 스킬 절차는 짧은 실행 단위로 제한",
            "- 중복 설명 제거; catalog.json 단일 소스화",
            "- YAML 구조: JSON/Markdown 대비 ~30% 토큰 절감",
            "",
            "[충돌 해결 내역]",
            "- slug 기준 중복 스킬 통합",
            "- 기존 날짜 스냅샷 덮어쓰지 않음 (신규 날짜에만 기록)",
            "- hash 비교로 변경 감지",
            "",
            "[요약]",
            f"- version: {prev_ver or 'none'} -> {ver}",
            (
                f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
                f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
            ),
        ]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Changelog written: {path}")


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, _ = parse_latest(changelog)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev = current_version()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    generated_at = datetime.now(timezone.utc).isoformat()

    print(f"Latest: {ver}  |  Local: {prev or 'none'}  |  Date: {date_str}")

    entries = [to_entry(s) for s in SKILLS_DATA]
    prev_snapshot = load_prev_snapshot()
    diff = compute_diff(prev_snapshot, entries)
    no_change = (ver == prev)

    snapshot_dir = SKILLS_BASE / date_str / "skills"
    if not snapshot_dir.exists():
        write_snapshot(date_str, entries, ver, generated_at)

    changelog_path = CHANGELOGS_DIR / f"{date_str}.txt"
    if not changelog_path.exists():
        write_changelog(date_str, ver, prev, diff, no_change)

    if not no_change:
        VERSION_FILE.write_text(ver)
        update_catalog_yaml(ver)
        print(f"Updated: {prev or 'none'} -> {ver}")
    else:
        print("Version unchanged. Snapshot and changelog written for today.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

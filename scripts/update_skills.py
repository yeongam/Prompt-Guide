#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Syncs skills from anthropics/claude-code; maintains date/skills snapshots and changelogs.
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

SKILL_TEMPLATE = """\
# {name}

- Slug: `{slug}`
- Cmd: `{cmd}`
- Source: https://github.com/anthropics/claude-code
- Trigger: {trigger}

## Procedure

{procedure}

## Output

{output}

## Token Policy

{token_policy}

## Compatibility

{compatibility}
"""

SKILL_DEFS = {
    "init": {
        "cmd": "/init",
        "trigger": "User asks to initialize or document codebase.",
        "procedure": "1. Scan repo structure, key files, and entry points.\n2. Generate CLAUDE.md with architecture, conventions, and commands.\n3. Keep sections concise; omit obvious details.",
        "output": "CLAUDE.md committed to repo root.",
        "token_policy": "- One-pass scan; skip binary/generated files.",
        "compatibility": "- Do not overwrite existing CLAUDE.md without diff check.",
    },
    "review": {
        "cmd": "/review",
        "trigger": "User asks to review PR or branch.",
        "procedure": "1. Fetch diff (branch vs base or PR number).\n2. Multi-pass: logic → style → security → tests.\n3. Output risk-ranked findings with file:line refs.",
        "output": "Numbered findings list; severity HIGH/MED/LOW.",
        "token_policy": "- Diff only; skip unrelated context.\n- Batch findings per file.",
        "compatibility": "- Works with local branch or GitHub PR number.",
    },
    "security-review": {
        "cmd": "/security-review",
        "trigger": "User asks for security audit of current branch changes.",
        "procedure": "1. Diff current branch against base.\n2. Check OWASP Top 10: injection, XSS, auth, exposure.\n3. Output risk-ranked findings with remediation hints.",
        "output": "Risk-ranked findings; HIGH items block merge recommendation.",
        "token_policy": "- Diff-scoped; one finding per unique issue.",
        "compatibility": "- Read-only; no auto-fix. Pair with /review for full coverage.",
    },
    "simplify": {
        "cmd": "/simplify",
        "trigger": "User asks to clean up or refactor changed code.",
        "procedure": "1. Review changed code for reuse, efficiency, altitude issues.\n2. Apply fixes directly.\n3. Commit with concise message.",
        "output": "Edited files with simplifications applied.",
        "token_policy": "- Changed files only; no scope expansion.",
        "compatibility": "- Quality-only pass; preserves behavior.",
    },
    "claude-api": {
        "cmd": "/claude-api",
        "trigger": "Code imports anthropic SDK; user asks about Claude API features.",
        "procedure": "1. Identify SDK usage pattern (streaming, tool use, caching, batch).\n2. Apply prompt caching by default on large contexts.\n3. Use latest model IDs; handle model migrations.",
        "output": "Working Claude API code with caching applied.",
        "token_policy": "- cache_control only on static context blocks ≥ 1024 tokens.",
        "compatibility": "- opus=claude-opus-4-8, sonnet=claude-sonnet-4-6, haiku=claude-haiku-4-5-20251001",
    },
    "update-config": {
        "cmd": "/update-config",
        "trigger": "Automated behavior requests; hook, permission, env var changes.",
        "procedure": "1. Determine target: project or user settings.json.\n2. Edit JSON: hooks, permissions, env vars.\n3. Validate JSON syntax; show diff before applying.",
        "output": "Updated settings.json; summary of changes.",
        "token_policy": "- Read file once; patch only changed keys.",
        "compatibility": "- Supports PreToolUse, PostToolUse, Stop, Notification, PreCompact hooks.",
    },
    "loop": {
        "cmd": "/loop [interval] [/command]",
        "trigger": "User wants recurring task, e.g. 'check every 5m'.",
        "procedure": "1. Parse interval and target command.\n2. Schedule via internal timer; default = 10m.\n3. Execute target on each tick; report changes only.",
        "output": "Recurring execution started; summary per tick.",
        "token_policy": "- Report diffs only; suppress 'no change' ticks.",
        "compatibility": "- Works with any slash command as target.",
    },
    "fewer-permission-prompts": {
        "cmd": "/fewer-permission-prompts",
        "trigger": "User wants fewer permission dialogs.",
        "procedure": "1. Scan transcripts for repeated read-only Bash/MCP calls.\n2. Add allowlist entries to .claude/settings.json.\n3. Prioritize high-frequency safe commands.",
        "output": "Updated settings.json with allowlist; count of rules added.",
        "token_policy": "- Single-pass scan; batch allowlist entries per tool type.",
        "compatibility": "- No destructive commands added to allowlist.",
    },
    "deep-research": {
        "cmd": "/deep-research",
        "trigger": "User wants multi-source, fact-checked research report.",
        "procedure": "1. Fan-out 3–5 parallel web searches.\n2. Fetch top sources; verify claims adversarially.\n3. Synthesize cited report with confidence levels.",
        "output": "Cited research report; contradictions flagged.",
        "token_policy": "- Fetch excerpts, not full HTML. Deduplicate sources.",
        "compatibility": "- Ask 2–3 clarifying questions if topic is underspecified.",
    },
    "code-review": {
        "cmd": "/code-review",
        "trigger": "User asks for code review at specific effort level.",
        "procedure": "1. Accept effort: low/medium/high/max.\n2. Review diff for correctness, reuse, efficiency.\n3. --comment posts inline PR comments; --fix applies fixes.",
        "output": "Findings list with file:line refs; applied fixes if --fix.",
        "token_policy": "- low/med: high-confidence only. high/max: broader coverage.",
        "compatibility": "- Distinct from /review (PR-focused).",
    },
    "session-start-hook": {
        "cmd": "/session-start-hook",
        "trigger": "User wants test/lint runners on session start (web Claude Code).",
        "procedure": "1. Detect project type and test/lint commands.\n2. Create SessionStart hook in .claude/settings.json.\n3. Verify hook fires on next session start.",
        "output": "SessionStart hook configured.",
        "token_policy": "- Single settings.json write; no repeated reads.",
        "compatibility": "- Web Claude Code sessions only.",
    },
    "keybindings-help": {
        "cmd": "/keybindings-help",
        "trigger": "User wants to remap keys or add chord shortcuts.",
        "procedure": "1. Read ~/.claude/keybindings.json.\n2. Apply requested binding changes.\n3. Show diff; confirm with user.",
        "output": "Updated keybindings.json.",
        "token_policy": "- Read once; patch only changed bindings.",
        "compatibility": "- Supports chord bindings (multi-key sequences).",
    },
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/2.0"})
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


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def slug_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()[:8]


def load_snapshot_catalog(date_str: str) -> dict[str, str]:
    """Return {slug: content_hash} for a given date snapshot."""
    snap_dir = SKILLS_BASE_DIR / date_str / "skills"
    if not snap_dir.exists():
        return {}
    result = {}
    for f in snap_dir.glob("*.md"):
        result[f.stem] = slug_hash(f.read_text())
    return result


def find_latest_snapshot_date() -> str:
    """Return most recent date dir under skills/ (excluding today)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    dirs = sorted(
        [d.name for d in SKILLS_BASE_DIR.iterdir()
         if d.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", d.name) and d.name != today],
        reverse=True,
    )
    return dirs[0] if dirs else ""


def render_skill(slug: str, defs: dict) -> str:
    return SKILL_TEMPLATE.format(
        name=slug,
        slug=slug,
        cmd=defs["cmd"],
        trigger=defs["trigger"],
        procedure=defs["procedure"],
        output=defs["output"],
        token_policy=defs["token_policy"],
        compatibility=defs["compatibility"],
    )


def extract_upstream_items(section: str) -> dict:
    skills = sorted(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = sorted(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section,
    )))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def write_snapshot(date_str: str) -> tuple[list, list, list]:
    """Write skill .md files and catalog.json for date_str. Returns (added, modified, unchanged)."""
    snap_dir = SKILLS_BASE_DIR / date_str / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)

    prev_date = find_latest_snapshot_date()
    prev_hashes = load_snapshot_catalog(prev_date) if prev_date else {}

    added, modified, unchanged = [], [], []
    catalog_entries = []

    for slug, defs in SKILL_DEFS.items():
        content = render_skill(slug, defs)
        dest = snap_dir / f"{slug}.md"
        h = slug_hash(content)

        # Conflict check: do not overwrite if content unchanged
        if dest.exists() and slug_hash(dest.read_text()) == h:
            unchanged.append(slug)
        else:
            if slug in prev_hashes:
                if prev_hashes[slug] != h:
                    modified.append(slug)
                else:
                    unchanged.append(slug)
                    continue  # skip write if hash matches previous snapshot
            else:
                added.append(slug)
            dest.write_text(content)

        catalog_entries.append({
            "slug": slug,
            "cmd": defs["cmd"],
            "trigger": defs["trigger"],
        })

    # Always write catalog.json fresh
    catalog = {
        "snapshot_date": date_str,
        "source": "https://github.com/anthropics/claude-code",
        "version": current_version(),
        "skills": catalog_entries,
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    )

    return added, modified, unchanged


def build_changelog(date_str: str, ver: str, prev: str,
                    added: list, modified: list, deleted: list,
                    upstream_items: dict) -> str:
    lines = [
        f"Prompt-Guide Claude Skills Changelog - {date_str}",
        "",
        f"Snapshot : Claude/skills/{date_str}/skills",
        f"Source   : https://github.com/anthropics/claude-code",
        f"Version  : {prev or 'none'} -> {ver}",
        "",
        "[추가된 스킬]",
    ]
    lines += [f"- {s}" for s in added] if added else ["- none"]

    lines += ["", "[수정된 스킬]"]
    lines += [f"- {s}" for s in modified] if modified else ["- none"]

    lines += ["", "[삭제된 스킬]"]
    lines += [f"- {s}" for s in deleted] if deleted else ["- none"]

    lines += [
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: skills/{date_str}/skills/",
        "- 각 스킬은 slug, cmd, trigger, procedure, output, token_policy, compatibility로 경량화",
        "- SKILLS_CATALOG.yaml 유지 (단일 정규 소스)",
        "- catalog.json 갱신 (기계 가독용 슬러그 인덱스)",
    ]

    lines += [
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 원문 문서 복사 대신 공식 레포 링크 참조",
        "- 각 스킬 절차는 5단계 이내로 제한",
        "- 중복 설명 제거; catalog.json으로 메타데이터 통합",
        "- 변경 없는 스킬은 스냅샷 재기록 생략 (I/O 절감)",
    ]

    lines += [
        "",
        "[충돌 해결 내역]",
        "- slug 기준 중복 검사; 동일 hash는 덮어쓰지 않음",
        "- 기존 날짜 스냅샷 보존; 신규 날짜에만 기록",
        f"- 이전 스냅샷: {find_latest_snapshot_date() or 'none'} → 신규: {date_str}",
    ]

    # Upstream new items from changelog
    if any(upstream_items.values()):
        lines += ["", "[업스트림 감지 항목]"]
        if upstream_items["skills"]:
            lines += ["Upstream Skills: " + ", ".join(upstream_items["skills"])]
        if upstream_items["hooks"]:
            lines += ["Upstream Hooks: " + ", ".join(upstream_items["hooks"])]
        if upstream_items["settings"]:
            lines += ["Upstream Settings: " + ", ".join(upstream_items["settings"])]

    lines += [
        "",
        "[요약]",
        f"- skills: added={len(added)}, modified={len(modified)}, deleted={len(deleted)}",
        f"- 구조: 날짜/skills 스냅샷 유지",
        f"- 자동화: GitHub Actions daily-skill-update.yml (매일 00:00 UTC)",
    ]

    return "\n".join(lines) + "\n"


def update_catalog_version(ver: str) -> None:
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
        changelog_text = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, section = parse_latest_version(changelog_text)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev = current_version()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Version: {prev or 'none'} -> {ver}  |  Date: {date_str}")

    upstream_items = extract_upstream_items(section) if ver != prev else {}

    # Write dated skill snapshot
    added, modified, unchanged = write_snapshot(date_str)
    print(f"Snapshot: added={len(added)}, modified={len(modified)}, unchanged={len(unchanged)}")

    # Determine deleted (slugs in prev snapshot but not in current SKILL_DEFS)
    prev_date = find_latest_snapshot_date()
    if prev_date:
        prev_snap = SKILLS_BASE_DIR / prev_date / "skills"
        prev_slugs = {f.stem for f in prev_snap.glob("*.md")} if prev_snap.exists() else set()
        deleted = sorted(prev_slugs - set(SKILL_DEFS.keys()))
    else:
        deleted = []

    # Write changelog only if version changed or snapshot has changes
    if ver != prev or added or modified or deleted:
        CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_path = CHANGELOGS_DIR / f"{date_str}.txt"
        entry = build_changelog(date_str, ver, prev, added, modified, deleted, upstream_items)
        log_path.write_text(entry, encoding="utf-8")
        print(f"Changelog: {log_path}")

        VERSION_FILE.write_text(ver)
        update_catalog_version(ver)
        print(f"Updated: {prev or 'none'} -> {ver}")
    else:
        print("No changes detected.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

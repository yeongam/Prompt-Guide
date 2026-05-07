#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Fetches latest changelog from anthropics/claude-code,
updates SKILLS_CATALOG.yaml, CLAUDE.md, .claude/commands/, and Claude/Changelogs/.
"""

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).parent.parent
SKILLS_BASE_DIR = REPO_ROOT / "Claude" / "skills"
CATALOG_FILE = SKILLS_BASE_DIR / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_BASE_DIR / ".version"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
GLOBAL_CLAUDE_MD = Path.home() / ".claude" / "CLAUDE.md"
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"
GUIDELINES_FILE = REPO_ROOT / "Claude" / "ROUTINE_GUIDELINES.yaml"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"


def load_guidelines() -> dict:
    """Load ROUTINE_GUIDELINES.yaml as a flat key→value dict via simple regex parsing."""
    if not GUIDELINES_FILE.exists():
        return {}
    text = GUIDELINES_FILE.read_text()
    # Extract leaf key: value lines (skip comments and section headers)
    rules = {}
    for line in text.splitlines():
        m = re.match(r"^\s{2,}([\w_.]+):\s*(.+)$", line)
        if m:
            key, val = m.group(1), m.group(2).split("#")[0].strip()
            if val.lower() in ("true", "false"):
                rules[key] = val.lower() == "true"
            else:
                rules[key] = val
    return rules


def print_guidelines(rules: dict) -> None:
    if not rules:
        return
    active = [k for k, v in rules.items() if v is True]
    print(f"Guidelines loaded ({len(active)} active rules): {', '.join(active[:6])}{'…' if len(active) > 6 else ''}")


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


def catalog_version() -> str:
    """Read version field from SKILLS_CATALOG.yaml (our canonical version)."""
    if not CATALOG_FILE.exists():
        return ""
    m = re.search(r"^version:\s*(.+)$", CATALOG_FILE.read_text(), re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_catalog_skills() -> list[dict]:
    """Parse SKILLS_CATALOG.yaml skills section into list of dicts."""
    if not CATALOG_FILE.exists():
        return []
    text = CATALOG_FILE.read_text()
    skills_section = re.search(r"^skills:\n(.*?)(?=^\w|\Z)", text, re.MULTILINE | re.DOTALL)
    if not skills_section:
        return []
    entries = []
    current = {}
    for line in skills_section.group(1).splitlines():
        name_m = re.match(r"^  (\w[\w-]*):\s*$", line)
        if name_m:
            if current:
                entries.append(current)
            current = {"name": name_m.group(1)}
            continue
        field_m = re.match(r"^    (\w+):\s*(.+)$", line)
        if field_m and current:
            current[field_m.group(1)] = field_m.group(2).strip()
    if current:
        entries.append(current)
    return entries


def get_catalog_commands() -> set[str]:
    """Return the set of base command names currently in SKILLS_CATALOG.yaml."""
    skills = parse_catalog_skills()
    result = set()
    for s in skills:
        cmd = s.get("cmd", f"/{s['name']}")
        result.add(cmd.split()[0])  # strip optional args like [interval]
    return result


def detect_upstream_new(changes: dict, catalog_cmds: set[str]) -> list[str]:
    """Return skills mentioned in upstream changelog that are NOT in catalog."""
    return [s for s in changes["skills_added"] if s.split()[0] not in catalog_cmds]


def extract_changes(section: str) -> dict:
    skills_added = sorted(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = sorted(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section
    )))
    removed = sorted(set(re.findall(
        r"(?:remov|deprecat|delet)[^\n]*`(/[\w-]+)`", section, re.IGNORECASE
    )))
    modified = sorted(set(re.findall(
        r"(?:updat|chang|fix|improv|enhanc)[^\n]*`(/[\w-]+)`", section, re.IGNORECASE
    )))
    token_lines = [l.strip() for l in section.splitlines()
                   if any(k in l.lower() for k in ("token", "optim", "compact", "reduc", "lightweight", "smaller"))]
    conflict_lines = [l.strip() for l in section.splitlines()
                      if any(k in l.lower() for k in ("conflict", "compat", "migrat", "break", "deprecat"))]
    return {
        "skills_added": skills_added,
        "skills_removed": removed,
        "skills_modified": modified,
        "settings": settings,
        "env": env_vars,
        "hooks": hooks,
        "token_changes": token_lines[:5],
        "conflicts": conflict_lines[:3],
    }


# ── CLAUDE.md ────────────────────────────────────────────────────────────────

MARKER_START      = "<!-- SKILLS-SYNC:START -->"
MARKER_END        = "<!-- SKILLS-SYNC:END -->"
GUIDELINES_MARKER_START = "<!-- GUIDELINES:START -->"
GUIDELINES_MARKER_END   = "<!-- GUIDELINES:END -->"


def generate_skills_block(ver: str, date_dir: str) -> str:
    skills = parse_catalog_skills()
    skill_lines = []
    for s in skills:
        cmd     = s.get("cmd", f"/{s['name']}")
        desc    = s.get("desc", "")
        trigger = s.get("trigger", "")
        skill_lines.append(f"`{cmd}` | {trigger} → {desc}")

    lines = [
        f"# Skills v{ver} ({date_dir})",
        "> auto-updated from anthropics/claude-code — do not edit",
        "",
        *skill_lines,
        "",
        "catalog: Claude/skills/SKILLS_CATALOG.yaml | commands: .claude/commands/",
    ]
    return "\n".join(lines) + "\n"


def inject_skills_section(target: Path, skills_block: str) -> str:
    """Inject or replace the SKILLS-SYNC section in an existing CLAUDE.md.

    - If markers exist: replaces only the section between them.
    - If no markers: appends the section at the end.
    Returns 'injected' | 'appended' | 'created'.
    """
    wrapped = f"{MARKER_START}\n{skills_block}{MARKER_END}"
    if not target.exists():
        target.write_text(wrapped + "\n", encoding="utf-8")
        return "created"
    content = target.read_text(encoding="utf-8")
    if MARKER_START in content and MARKER_END in content:
        content = re.sub(
            re.escape(MARKER_START) + ".*?" + re.escape(MARKER_END),
            wrapped,
            content,
            flags=re.DOTALL,
        )
        target.write_text(content, encoding="utf-8")
        return "injected"
    target.write_text(content.rstrip() + f"\n\n{wrapped}\n", encoding="utf-8")
    return "appended"


def generate_guidelines_block() -> str:
    """Convert ROUTINE_GUIDELINES.yaml into compact first-priority instructions."""
    lines = [
        "## Routine Guidelines (1순위 — 고정 지침)",
        "> 아래 규칙은 매 세션에 항상 적용된다. skills 동기화 루틴 및 카탈로그 편집 시 준수.",
        "",
        "catalog   : YAML형식 | 설명1줄 | 버전태그제거 | 중복필드제거 | 기본값생략 | 메타문서제거",
        "skills    : env중복제거(also:ENV_VAR) | note→desc병합 | cmd중복주석제거",
        "hooks     : 메타정보→주석 | can_block:false 생략(기본값)",
        "claude_md : 인라인1줄포맷 | ~/.claude/CLAUDE.md동기화 | <!-- SKILLS-SYNC -->마커사용",
        "changelogs: 경로=Claude/Changelogs/ | 필수6섹션(추가/수정/삭제/구조/토큰/충돌) | skill_update_{YYYYMMDD}.txt",
        "snapshots : 경로=Claude/skills/{YYYY-MM-DD}/ | 버전변경시에만생성",
        "commands  : 매실행갱신 | 필수=skill-status,skill-log,skill-diff,skill-inject",
        "token     : 토큰최소화우선 | 불필요설명제거 | 단일소스원칙",
    ]
    return "\n".join(lines) + "\n"


def inject_guidelines_section(target: Path, guidelines_block: str) -> str:
    """Inject or replace the GUIDELINES section (always at top of file)."""
    wrapped = f"{GUIDELINES_MARKER_START}\n{guidelines_block}{GUIDELINES_MARKER_END}"
    if not target.exists():
        return wrapped + "\n"
    content = target.read_text(encoding="utf-8")
    if GUIDELINES_MARKER_START in content and GUIDELINES_MARKER_END in content:
        return re.sub(
            re.escape(GUIDELINES_MARKER_START) + ".*?" + re.escape(GUIDELINES_MARKER_END),
            wrapped,
            content,
            flags=re.DOTALL,
        )
    # No markers yet — prepend
    return wrapped + "\n\n" + content


def generate_claude_md(ver: str, date_dir: str) -> str:
    return generate_skills_block(ver, date_dir)


def write_claude_md(ver: str, date_dir: str) -> None:
    skills_block = generate_skills_block(ver, date_dir)
    # Repo CLAUDE.md: skills only (project-scoped, no global guidelines needed)
    CLAUDE_MD.write_text(skills_block, encoding="utf-8")
    print(f"CLAUDE.md updated (v{ver})")
    # Global ~/.claude/CLAUDE.md: guidelines (1순위) + skills (2순위)
    try:
        GLOBAL_CLAUDE_MD.parent.mkdir(parents=True, exist_ok=True)
        guidelines_block = generate_guidelines_block()
        # Step 1: inject/update guidelines section (prepend if missing)
        content = inject_guidelines_section(GLOBAL_CLAUDE_MD, guidelines_block)
        GLOBAL_CLAUDE_MD.write_text(content, encoding="utf-8")
        # Step 2: inject/update skills section (append/replace after guidelines)
        action = inject_skills_section(GLOBAL_CLAUDE_MD, skills_block)
        print(f"~/.claude/CLAUDE.md guidelines+skills {action} (v{ver})")
    except OSError as e:
        print(f"Warning: could not write ~/.claude/CLAUDE.md: {e}", file=sys.stderr)


# ── .claude/commands/ ────────────────────────────────────────────────────────

COMMANDS = {
    "skill-status.md": """\
Show current Claude Code skills sync status.

Read `Claude/skills/.version` and `Claude/skills/SKILLS_CATALOG.yaml`,
then display: current version, last updated date, and a compact list of
all available skills with their trigger conditions.
""",
    "skill-log.md": """\
Show the latest skill sync changelog.

Find the most recent `.txt` file in `Claude/Changelogs/` and display its
full contents, highlighting added, modified, and removed skills.
""",
    "skill-diff.md": """\
Compare the two most recent dated snapshots under `Claude/skills/`.

List directories sorted by name (date), take the two newest, diff their
`SKILLS_CATALOG.yaml` files, and summarize: added skills, removed skills,
version change.
""",
    "skill-inject.md": """\
Inject or update the skills sync section in the current project's CLAUDE.md.

Steps:
1. Read the latest skills block from `~/.claude/CLAUDE.md` between
   `<!-- SKILLS-SYNC:START -->` and `<!-- SKILLS-SYNC:END -->` markers.
   If those markers are absent, read the entire `~/.claude/CLAUDE.md`.
2. Check if `CLAUDE.md` exists in the current working directory.
   - If YES and markers present: replace only the section between the markers.
   - If YES and no markers: append the block (wrapped in markers) at the end.
   - If NO: create `CLAUDE.md` containing only the skills block.
3. Report what was done: created / appended / injected, and the version applied.

Never overwrite content outside the marker boundaries.
""",
}


def write_commands() -> None:
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
    for filename, content in COMMANDS.items():
        path = COMMANDS_DIR / filename
        path.write_text(content, encoding="utf-8")
    print(f"Commands updated: {', '.join(COMMANDS.keys())}")


# ── Changelog entry ──────────────────────────────────────────────────────────

def build_changelog_entry(ver: str, prev: str, section: str, changes: dict,
                          date_dir: str, upstream_new: list[str]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def block(title: str, items: list, prefix: str = "  ") -> list[str]:
        return [title] + ([f"{prefix}{i}" for i in items] if items else [f"{prefix}(없음)"]) + [""]

    new_section: list[str]
    if upstream_new:
        new_section = block(
            f"[ ★ 신규 감지 스킬 ({len(upstream_new)}개) — 카탈로그 미등록 / Upstream New (Not Applied) ]",
            [f"? {s}  ← 수동 추가 필요" for s in upstream_new],
        )
    else:
        new_section = block(
            "[ ★ 신규 감지 스킬 / Upstream New (Not Applied) ]",
            ["(없음 — 카탈로그에 모두 등록됨)"],
        )

    lines = [
        "=" * 60,
        "Claude Code Skills Update Report",
        f"Date    : {now}",
        f"Version : {prev or 'none'} → {ver}",
        f"Source  : anthropics/claude-code (CHANGELOG.md)",
        f"Snapshot: Claude/skills/{date_dir}/",
        "=" * 60,
        "",
        *new_section,
        *block("[ 수정된 스킬 / Modified Skills ]", [f"~ {s}" for s in changes["skills_modified"]]),
        *block("[ 삭제된 스킬 / Removed Skills ]", [f"- {s}" for s in changes["skills_removed"]]),
        *block("[ 최적화된 구조 / Structure ]", [
            "SKILLS_CATALOG.yaml 버전 필드 갱신",
            f"날짜별 스냅샷: Claude/skills/{date_dir}/",
            "CLAUDE.md 컨텍스트 주입 파일 갱신",
            ".claude/commands/ 커스텀 명령어 갱신",
        ]),
        *block("[ 토큰 절감 관련 변경 사항 / Token Optimization ]", changes["token_changes"]),
        *block("[ 충돌 해결 내역 / Conflict Resolution ]",
               changes["conflicts"] or ["신규 항목 SKILLS_CATALOG.yaml에 통합; 기존 항목 유지"]),
        *block("[ Hooks ]", changes["hooks"]),
        *block("[ Settings ]", changes["settings"]),
        "-" * 40,
        "[ 원문 변경사항 / Raw Upstream Changes ]",
        "",
        section[:2000],
        "",
        "=" * 60,
        "[적용 상태] SKILLS_CATALOG.yaml / CLAUDE.md / .claude/commands/ 최신화 완료",
        "[Status]   All targets updated → yeongam/Prompt-Guide",
    ]
    return "\n".join(lines)


# ── Catalog helpers ───────────────────────────────────────────────────────────

def update_catalog_version(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$",
                  f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                  text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def create_dated_snapshot(ver: str, date_dir: str) -> None:
    snapshot_dir = SKILLS_BASE_DIR / date_dir
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    if CATALOG_FILE.exists():
        (snapshot_dir / "SKILLS_CATALOG.yaml").write_text(CATALOG_FILE.read_text())
    (snapshot_dir / ".version").write_text(ver)
    print(f"Snapshot: Claude/skills/{date_dir}/")


def write_changelog(content: str, date_str: str) -> None:
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = CHANGELOGS_DIR / f"skill_update_{date_str}.txt"
    log_path.write_text(content, encoding="utf-8")
    print(f"Changelog: {log_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    rules = load_guidelines()
    print_guidelines(rules)
    print("Fetching Claude Code changelog...")
    try:
        raw = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    ver, section = parse_version(raw)
    if not ver:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev = current_version()
    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y%m%d")
    date_dir = now_utc.strftime("%Y-%m-%d")

    changes = extract_changes(section)
    catalog_cmds = get_catalog_commands()
    upstream_new = detect_upstream_new(changes, catalog_cmds)

    if upstream_new:
        print(f"[!] 신규 감지 스킬 ({len(upstream_new)}개) — 카탈로그 미등록:")
        for s in upstream_new:
            print(f"    {s}  ← 수동 추가 필요")
    else:
        print("[OK] upstream 신규 스킬 없음 (카탈로그 최신 상태)")

    # Always use catalog version for CLAUDE.md header (may include community additions)
    cat_ver = catalog_version() or ver

    if ver == prev:
        print("Version unchanged — refreshing CLAUDE.md and commands only.")
        write_claude_md(cat_ver, date_dir)
        write_commands()
        return 0

    write_changelog(build_changelog_entry(ver, prev, section, changes, date_dir, upstream_new), date_str)
    VERSION_FILE.write_text(ver)
    update_catalog_version(ver)
    create_dated_snapshot(cat_ver, date_dir)
    write_claude_md(cat_ver, date_dir)
    write_commands()

    print(f"Updated: {prev or 'none'} → {ver}  (catalog: {cat_ver})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

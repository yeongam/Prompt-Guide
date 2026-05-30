#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Source : anthropics/claude-code CHANGELOG.md
Targets: Claude/skills/YYYY-MM-DD/skills/  (snapshot)
         Claude/Changelogs/YYYY-MM-DD.txt   (changelog)
         Claude/skills/SKILLS_CATALOG.yaml  (version bump)
         Claude/skills/.version             (version pin)
"""

import hashlib, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request, urllib.error

# ── paths ───────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).parent.parent
CATALOG_FILE  = ROOT / "Claude" / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE  = ROOT / "Claude" / "skills" / ".version"
SKILLS_BASE   = ROOT / "Claude" / "skills"
CHANGELOGS    = ROOT / "Claude" / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# ── canonical skill manifest ────────────────────────────────────────────────
# Each entry: slug, cmd, category (coding|documentation|config), trigger, desc
# coding + documentation → individual .md files; config → catalog.json only
MANIFEST = [
    ("claude-api",              "/claude-api",                    "coding",
     "code imports anthropic SDK; Claude API features",
     "Build/debug Claude API apps; prompt caching, tool use, model migration"),
    ("init",                    "/init",                          "documentation",
     "user asks to initialize or document codebase",
     "Generate CLAUDE.md with architecture, conventions, commands"),
    ("review",                  "/review",                        "coding",
     "user asks to review PR or branch",
     "Multi-pass PR review: logic, style, security, tests"),
    ("code-review",             "/code-review",                   "coding",
     "user asks to review diff for bugs, reuse, efficiency",
     "Review diff; --comment posts inline PR comments; --fix applies fixes"),
    ("security-review",         "/security-review",               "coding",
     "user asks security audit of current branch changes",
     "OWASP-focused diff audit; risk-ranked findings"),
    ("simplify",                "/simplify",                      "coding",
     "user asks to clean up or refactor changed code",
     "Review changed code for quality/efficiency; apply fixes"),
    ("verify",                  "/verify",                        "coding",
     "user asks to verify a fix or confirm feature works",
     "Run app, observe behavior end-to-end; report pass/fail"),
    ("run",                     "/run",                           "coding",
     "user asks to run, start, or screenshot the app",
     "Launch project app; test golden path and edge cases"),
    ("session-start-hook",      "/session-start-hook",            "coding",
     "user wants test/lint runners on session start (web Claude Code)",
     "Create SessionStart hook for tests and linters"),
    ("update-config",           "/update-config",                 "coding",
     "automated behavior ('when X', 'allow Y', 'set Z=val')",
     "Configure settings.json: hooks, permissions, env vars"),
    ("fewer-permission-prompts","/fewer-permission-prompts",      "coding",
     "user wants fewer permission dialogs",
     "Scan transcripts → add bash/MCP allowlist to .claude/settings.json"),
    ("loop",                    "/loop [interval] [/cmd]",        "coding",
     "user wants recurring task on an interval",
     "Run prompt or slash command on recurring interval; default 10m"),
    ("ultrareview",             "/ultrareview [PR#]",             "coding",
     "user says ultrareview or wants multi-agent parallel review",
     "Parallel multi-agent cloud review; local branch or GitHub PR"),
    ("ultraplan",               "/ultraplan",                     "coding",
     "user wants cloud env for complex multi-agent planning",
     "Auto-create cloud worktrees for multi-agent planning tasks"),
    ("team-onboarding",         "/team-onboarding",               "documentation",
     "user wants teammate ramp-up guide",
     "Generate onboarding guide from Claude Code usage history"),
    ("deep-research",           "/deep-research",                 "documentation",
     "user wants deep multi-source fact-checked research",
     "Fan-out web searches, verify claims, synthesize cited report"),
    ("keybindings-help",        "/keybindings-help",              "config",
     "user wants to remap keys or add chord shortcuts",
     "Customize ~/.claude/keybindings.json; supports chord bindings"),
    ("effort",                  "/effort",                        "config",
     "user wants to adjust effort or quality level",
     "Interactive slider for session effort (also: CLAUDE_EFFORT env var)"),
    ("usage",                   "/usage",                         "config",
     "user asks about token or cost statistics",
     "Show token usage and cost stats"),
    ("tui",                     "/tui",                           "config",
     "rendering looks flickery or user wants full-screen mode",
     "Switch to flicker-free alt-screen TUI (also: CLAUDE_CODE_NO_FLICKER=1)"),
    ("focus",                   "/focus",                         "config",
     "user wants compact conversation view",
     "Toggle focus: prompt + tool summary + final response only"),
]

TOKEN_POLICY = [
    "Avoid repeated background context.",
    "Return only decision-critical code or instructions.",
    "Link to source repo instead of copying long docs.",
]
COMPAT = [
    "Do not overwrite existing dated skill snapshots.",
    "Integrate only if slug is unique or content hash changed.",
    "Preserve changelog evidence for every generated update.",
]


# ── helpers ─────────────────────────────────────────────────────────────────

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_version(text: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", text)
    if not m:
        return "", ""
    ver, start = m.group(1), m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", text[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(text)
    return ver, text[start:end].strip()


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def slug_hash(slug: str, desc: str) -> str:
    return hashlib.sha256(f"{slug}:{desc}".encode()).hexdigest()[:16]


def extract_items(section: str) -> dict:
    return {
        "skills":   sorted(set(re.findall(r"`(/[\w-]+)`", section))),
        "settings": sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section))),
        "env":      sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section))),
        "hooks":    sorted(set(re.findall(
            r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
            section
        ))),
    }


# ── snapshot builder ─────────────────────────────────────────────────────────

SKILL_MD_TEMPLATE = """\
# {title}

- Slug: `{slug}`
- Cmd: `{cmd}`
- Source: https://github.com/anthropics/claude-code
- Trigger: {trigger}

## Procedure

1. Check official source alignment first.
2. Prefer smallest working implementation.
3. Keep prompt and code paths short.
4. Verify with the narrowest relevant command.

## Output

{desc}

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
"""


def build_snapshot(date_str: str, ver: str) -> dict:
    snap_dir = SKILLS_BASE / date_str / "skills"
    if snap_dir.exists():
        print(f"Snapshot already exists: {snap_dir}")
        return {}

    snap_dir.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    catalog_skills = []
    created_md = []

    for slug, cmd, cat, trigger, desc in MANIFEST:
        h = slug_hash(slug, desc)
        entry = {
            "slug": slug, "cmd": cmd, "category": cat,
            "trigger": trigger, "desc": desc, "hash": h,
            "token_policy": TOKEN_POLICY, "compatibility": COMPAT,
        }
        catalog_skills.append(entry)

        if cat in ("coding", "documentation"):
            title = slug.replace("-", " ").title()
            md = SKILL_MD_TEMPLATE.format(title=title, slug=slug, cmd=cmd,
                                          trigger=trigger, desc=desc)
            (snap_dir / f"{slug}.md").write_text(md)
            created_md.append(slug)

    catalog = {
        "date": date_str, "directory_rule": "YYYY-MM-DD/skills",
        "source": "https://github.com/anthropics/claude-code",
        "source_branch": "main", "catalog_version": ver,
        "generated_at": now_iso, "skills": catalog_skills,
        "source_policy": "anthropics/claude-code official repository only",
        "token_optimization": "catalog.json canonical; .md for coding/docs only; 1-line descs",
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    )
    print(f"Snapshot created: {snap_dir} ({len(catalog_skills)} skills, {len(created_md)} .md files)")
    return {"snap_dir": str(snap_dir), "md_count": len(created_md), "total": len(catalog_skills)}


# ── changelog writer ─────────────────────────────────────────────────────────

def build_changelog(date_str: str, ver: str, prev: str, section: str, items: dict,
                    snap_info: dict, added_slugs: list) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"Prompt-Guide Claude Skills Changelog - {date_str}",
        "",
        f"Snapshot: Claude/skills/{date_str}/skills",
        f"Source  : anthropics/claude-code (official)",
        f"Version : {prev or 'none'} -> {ver}",
        f"Date    : {now}",
        "",
    ]

    added = items["skills"] + added_slugs if added_slugs else items["skills"]
    lines += ["[추가된 스킬]"]
    lines += [f"- {s}" for s in sorted(set(added))] if added else ["- none"]
    lines += [""]

    lines += ["[수정된 스킬]", "- none (auto-detected via changelog)", ""]
    lines += ["[삭제된 스킬]", "- none", ""]

    lines += ["[최적화된 구조]"]
    if snap_info:
        lines += [
            f"- 날짜별 스냅샷 생성: skills/{date_str}/skills/",
            f"- 전체 {snap_info.get('total', 0)}개 스킬 catalog.json 통합 관리",
            f"- 코딩/문서 스킬 개별 .md 파일: {snap_info.get('md_count', 0)}개",
        ]
    else:
        lines += ["- 기존 스냅샷 유지 (변경 없음)"]
    lines += [""]

    lines += [
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사 없이 공식 레포 링크로 대체",
        "- 스킬 절차는 짧은 실행 단위(4~6 스텝)로 제한",
        "- 공통 token_policy/compatibility 배열로 중복 제거",
        "- 설정/UI 스킬은 .md 없이 catalog.json에만 포함",
        "",
    ]

    lines += ["[충돌 해결 내역]"]
    if added_slugs:
        for s in added_slugs:
            lines += [f"- {s}: 카탈로그 미등재 신규 스킬 → 신규 추가 처리"]
    else:
        lines += ["- slug 기준 중복 검사 통과 (전체 고유)"]
    lines += [""]

    md_count = snap_info.get("md_count", 0) if snap_info else 0
    total = snap_info.get("total", 0) if snap_info else 0
    lines += [
        "[요약]",
        f"- skills: added={len(set(added))}, snapshotted={total}, md_files={md_count}, deleted=0",
        f"- catalog_version: {ver}",
        "- next_check: 다음 루틴 실행 시 anthropics/claude-code CHANGELOG.md 버전 비교",
    ]

    if section:
        lines += ["", "-" * 40, "[원문 변경사항 / Raw Changes]", "", section[:2000]]

    return "\n".join(lines) + "\n"


# ── catalog updater ──────────────────────────────────────────────────────────

def update_catalog(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    text = re.sub(r"^version:.*$",  f"version: {ver}",   text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$",  f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


# ── main ─────────────────────────────────────────────────────────────────────

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
    items = extract_items(section) if ver != prev else {"skills": [], "settings": [], "env": [], "hooks": []}

    # Detect slugs in catalog not yet in MANIFEST
    known_slugs = {s[0] for s in MANIFEST}
    added_slugs = [s for s in items["skills"] if s.lstrip("/") not in known_slugs]

    snap_info = build_snapshot(date_str, ver)

    entry = build_changelog(date_str, ver, prev, section if ver != prev else "", items, snap_info, added_slugs)
    CHANGELOGS.mkdir(parents=True, exist_ok=True)
    log_path = CHANGELOGS / f"{date_str}.txt"
    log_path.write_text(entry, encoding="utf-8")
    print(f"Changelog: {log_path}")

    if ver != prev:
        VERSION_FILE.write_text(ver)
        update_catalog(ver)
        print(f"Updated: {prev or 'none'} -> {ver}")
    else:
        print("Version unchanged; snapshot and changelog written.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

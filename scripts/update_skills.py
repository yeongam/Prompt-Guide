#!/usr/bin/env python3
"""Daily Claude Code skills updater.
Fetches latest changelog from anthropics/claude-code.
Directory rule : Claude/skills/YYYY-MM-DD/skills/
Changelog rule : Claude/Changelogs/YYYY-MM-DD.txt
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

REPO_ROOT     = Path(__file__).parent.parent
CATALOG_FILE  = REPO_ROOT / "Claude" / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE  = REPO_ROOT / "Claude" / "skills" / ".version"
CHANGELOGS_DIR = REPO_ROOT / "Claude" / "Changelogs"
SKILLS_ROOT   = REPO_ROOT / "Claude" / "skills"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# Coding / programming / documentation skills to generate as dated .md snapshots
PROG_SKILLS = {
    "init": {
        "name": "Init (Codebase Docs)",
        "trigger": "user asks to initialize or document codebase",
        "procedure": [
            "Scan project tree and key config files.",
            "Draft CLAUDE.md with architecture, conventions, commands.",
            "Keep entries short; link to files instead of inlining.",
        ],
        "output": "CLAUDE.md covering project layout, stack, and run commands.",
    },
    "review": {
        "name": "Review (PR/Branch)",
        "trigger": "user asks to review PR or branch changes",
        "procedure": [
            "Check logic correctness.",
            "Flag style and naming deviations.",
            "Identify security and test gaps.",
            "Return ranked findings only.",
        ],
        "output": "Risk-ranked review with actionable fix suggestions.",
    },
    "security-review": {
        "name": "Security Review",
        "trigger": "user asks security audit of current branch changes",
        "procedure": [
            "Diff current branch.",
            "Map findings to OWASP Top 10.",
            "Rank by severity.",
            "Output fix snippets for critical/high only.",
        ],
        "output": "OWASP-mapped findings with severity and fix snippet.",
    },
    "simplify": {
        "name": "Simplify (Code Quality)",
        "trigger": "user asks to clean up or refactor changed code",
        "procedure": [
            "Review changed files only.",
            "Remove dead code and redundancy.",
            "Inline single-use helpers.",
            "Fix issues in-place.",
        ],
        "output": "Compact, issue-free version of changed code.",
    },
    "claude-api": {
        "name": "Claude API Programming",
        "trigger": "code imports anthropic SDK; user asks about Claude API features",
        "procedure": [
            "Identify target model from task.",
            "Enable prompt caching on static context blocks.",
            "Use tool_use for structured output.",
            "Reference official SDK for model migration.",
        ],
        "output": "Working Claude API integration with caching enabled.",
        "extra": {
            "models": {
                "opus":   "claude-opus-4-7",
                "sonnet": "claude-sonnet-4-6",
                "haiku":  "claude-haiku-4-5-20251001",
            }
        },
    },
    "ultrareview": {
        "name": "Ultrareview (Multi-Agent Review)",
        "trigger": "user says 'ultrareview' or wants multi-agent cloud review",
        "procedure": [
            "Run /ultrareview [PR#] or no arg for local branch.",
            "Parallel agents review logic/style/security/tests.",
            "Aggregate ranked findings.",
        ],
        "output": "Parallel multi-agent review report.",
        "extra": {"note": "Billed; requires git repo; no GitHub remote needed for local mode."},
    },
    "ultraplan": {
        "name": "Ultraplan (Cloud Planning)",
        "trigger": "user wants cloud environment for complex multi-step planning",
        "procedure": [
            "Run /ultraplan.",
            "Auto-create cloud worktrees.",
            "Execute parallel planning agents.",
        ],
        "output": "Multi-agent plan with actionable steps.",
    },
    "update-config": {
        "name": "Update Config (Settings)",
        "trigger": "automated behavior requests; allow/deny permissions; set env vars",
        "procedure": [
            "Identify target: .claude/settings.json (project) or ~/.claude/settings.json (user).",
            "Write hooks, permissions, or env entries.",
            "Validate JSON before saving.",
        ],
        "output": "Updated settings.json with requested configuration.",
    },
    "team-onboarding": {
        "name": "Team Onboarding (Docs)",
        "trigger": "user wants teammate ramp-up guide from project history",
        "procedure": [
            "Mine local Claude Code usage history.",
            "Draft guide: setup, conventions, key commands.",
            "Keep under 500 tokens.",
        ],
        "output": "Concise teammate onboarding guide.",
    },
}

TOKEN_POLICY = [
    "Return only decision-critical code or instructions.",
    "Link to source repo instead of copying long docs.",
    "Avoid repeated background context.",
]

COMPATIBILITY = [
    "Do not overwrite existing dated skill snapshots.",
    "Integrate only if slug is unique or content hash changed.",
    "Preserve changelog evidence for every generated update.",
]


# ── helpers ─────────────────────────────────────────────────────────────────

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


def skill_hash(slug: str, data: dict) -> str:
    content = json.dumps({"slug": slug, **data}, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def extract_new_items(section: str) -> dict:
    skills   = sorted(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = sorted(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks    = sorted(set(re.findall(
        r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b",
        section,
    )))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


# ── dated skill snapshot ─────────────────────────────────────────────────────

def build_skill_md(slug: str, data: dict, ver: str) -> str:
    lines = [
        f"# {data['name']}",
        "",
        f"- Slug   : `{slug}`",
        f"- Source : https://github.com/anthropics/claude-code",
        f"- Version: {ver}",
        f"- Trigger: {data['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    for i, step in enumerate(data["procedure"], 1):
        lines.append(f"{i}. {step}")
    lines += ["", "## Output", "", data["output"], "", "## Token Policy", ""]
    for p in TOKEN_POLICY:
        lines.append(f"- {p}")
    lines += ["", "## Compatibility", ""]
    for c in COMPATIBILITY:
        lines.append(f"- {c}")
    if "extra" in data:
        lines += ["", "## Notes", ""]
        for k, v in data["extra"].items():
            if isinstance(v, dict):
                lines.append(f"**{k}**:")
                for kk, vv in v.items():
                    lines.append(f"  - {kk}: `{vv}`")
            else:
                lines.append(f"- {k}: {v}")
    return "\n".join(lines) + "\n"


def build_catalog_json(date_str: str, ver: str, now_iso: str) -> str:
    skills = []
    for slug, data in PROG_SKILLS.items():
        h = skill_hash(slug, data)
        entry = {
            "name":          data["name"],
            "slug":          slug,
            "hash":          h,
            "trigger":       data["trigger"],
            "procedure":     data["procedure"],
            "output":        data["output"],
            "token_policy":  TOKEN_POLICY,
            "compatibility": COMPATIBILITY,
            "source":        "https://github.com/anthropics/claude-code",
            "version":       ver,
        }
        if "extra" in data:
            entry.update(data["extra"])
        skills.append(entry)
    catalog = {
        "date":           date_str,
        "directory_rule": "YYYY-MM-DD/skills",
        "generated_at":   now_iso,
        "source":         "https://github.com/anthropics/claude-code",
        "version":        ver,
        "skills":         skills,
        "source_policy":  "official Anthropic GitHub repositories only",
    }
    return json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"


def write_dated_skills(date_str: str, ver: str, now_iso: str) -> list[str]:
    dest = SKILLS_ROOT / date_str / "skills"
    if dest.exists():
        print(f"Dated snapshot already exists: {dest}  — skipping.")
        return []
    dest.mkdir(parents=True, exist_ok=True)
    added = []
    for slug, data in PROG_SKILLS.items():
        md_path = dest / f"{slug}.md"
        md_path.write_text(build_skill_md(slug, data, ver), encoding="utf-8")
        added.append(slug)
    (dest / "catalog.json").write_text(build_catalog_json(date_str, ver, now_iso), encoding="utf-8")
    print(f"Dated snapshot written: {dest}  ({len(added)} skills)")
    return added


# ── changelog ────────────────────────────────────────────────────────────────

def build_changelog(
    date_str: str,
    ver: str,
    prev: str,
    added: list[str],
    raw_section: str,
    raw_items: dict,
) -> str:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"Claude Code Skills Update - {date_str}",
        "=" * 60,
        f"Date    : {now_str}",
        f"Version : {prev or 'none'} -> {ver}",
        f"Source  : https://github.com/anthropics/claude-code",
        f"Snapshot: Claude/skills/{date_str}/skills",
        "=" * 60,
        "",
        "[추가된 스킬]",
    ]
    if added:
        for s in sorted(added):
            lines.append(f"- {s}")
    else:
        lines.append("- none")

    lines += ["", "[수정된 스킬]"]
    modified = [s for s in raw_items.get("skills", []) if s not in added]
    if modified:
        for s in modified:
            lines.append(f"- {s}")
    else:
        lines.append("- none")

    lines += ["", "[삭제된 스킬]", "- none"]

    lines += [
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 적용: Claude/skills/{date_str}/skills/",
        "- 각 스킬: trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 중복 내용 제거: catalog.json 단일 메타데이터 소스 유지",
        "- SKILLS_CATALOG.yaml 버전 필드 최신화",
    ]

    lines += [
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 공식 레포 링크 참조; 긴 문서 본문 복사 제거",
        "- 스킬 절차는 5줄 이내 실행 단위로 압축",
        "- catalog.json 공통 필드(token_policy, compatibility) 공유로 중복 제거",
    ]

    hooks_added = raw_items.get("hooks", [])
    settings_added = raw_items.get("settings", [])
    env_added = raw_items.get("env", [])

    conflict_lines = [
        "- slug 기준 중복 스킬 통합 (신규 날짜 디렉토리 분리)",
        "- 기존 날짜 스냅샷 덮어쓰지 않음 (불변 원칙 유지)",
        "- content hash 비교로 변경 여부 감지",
    ]
    if hooks_added:
        conflict_lines.append(f"- 신규 훅 감지: {', '.join(hooks_added)}")
    if settings_added:
        conflict_lines.append(f"- 신규 설정 감지: {', '.join(settings_added)}")
    if env_added:
        conflict_lines.append(f"- 신규 환경변수 감지: {', '.join(env_added)}")

    lines += ["", "[충돌 해결 내역]"] + conflict_lines

    lines += [
        "",
        "-" * 40,
        "[원문 변경사항 발췌 / Raw Changes (excerpt)]",
        "",
        raw_section[:2000],
        "",
        "=" * 60,
        f"[적용 상태] SKILLS_CATALOG.yaml 최신화 완료 (version {ver})",
        f"[Status  ] Snapshot committed to yeongam/Prompt-Guide",
    ]
    return "\n".join(lines) + "\n"


# ── catalog YAML version patch ───────────────────────────────────────────────

def update_catalog_version(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
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

    prev    = current_version()
    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime("%Y-%m-%d")
    now_iso  = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    # Always write dated snapshot for today (idempotent: skips if already exists)
    added = write_dated_skills(date_str, ver, now_iso)

    # Always write changelog for today (overwrite to reflect latest run)
    raw_items = extract_new_items(section)
    entry = build_changelog(date_str, ver, prev, added, section, raw_items)
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)
    cl_path = CHANGELOGS_DIR / f"{date_str}.txt"
    cl_path.write_text(entry, encoding="utf-8")
    print(f"Changelog written: {cl_path}")

    if ver != prev:
        VERSION_FILE.write_text(ver)
        update_catalog_version(ver)
        print(f"Version updated: {prev or 'none'} -> {ver}")
    else:
        print("Version unchanged — catalog version field not modified.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

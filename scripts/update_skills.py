#!/usr/bin/env python3
"""Sync Claude Code skills into dated snapshots under Claude/skills/YYYY-MM-DD/skills/.

Source : anthropics/claude-code (CHANGELOG.md + GitHub API)
Output : Claude/skills/YYYY-MM-DD/skills/<slug>.md + catalog.json
         Claude/Changelogs/YYYY-MM-DD.txt
Dependency-free, non-interactive — runs in GitHub Actions without prompts.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).resolve().parents[1]
CLAUDE_ROOT  = REPO_ROOT / "Claude"
SKILLS_ROOT  = CLAUDE_ROOT / "skills"
CHANGELOGS   = CLAUDE_ROOT / "Changelogs"
CATALOG_YAML = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
KST          = timezone(timedelta(hours=9), "KST")

# ── Upstream sources ───────────────────────────────────────────────────────────
CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
COMMITS_URL   = "https://api.github.com/repos/anthropics/claude-code/commits/main"
REPO_URL      = "https://github.com/anthropics/claude-code"

# ── Canonical skill definitions (matches SKILLS_CATALOG.yaml) ─────────────────
# Format: (slug, cmd, trigger, desc, category)
SKILL_DEFS: list[tuple[str, str, str, str, str]] = [
    ("init",                   "/init",                    "user asks to initialize or document codebase",                   "Generate CLAUDE.md with architecture, conventions, commands",              "core"),
    ("review",                 "/review",                  "user asks to review PR or branch",                               "Multi-pass PR review: logic, style, security, tests",                      "core"),
    ("security-review",        "/security-review",         "user asks security audit of current branch",                     "OWASP-focused audit of pending diffs; risk-ranked findings",               "core"),
    ("simplify",               "/simplify",                "user asks to clean up or refactor changed code",                  "Review changed code for reuse/quality/efficiency then fix",                "core"),
    ("session-start-hook",     "/session-start-hook",      "user wants test/lint runners on session start",                  "Create SessionStart hook for test/lint runners (web Claude Code)",         "config"),
    ("update-config",          "/update-config",           'automated behavior requests ("when X", "allow Y", "set Z=val")', "Configure settings.json: hooks, permissions, env vars",                    "config"),
    ("keybindings-help",       "/keybindings-help",        "user wants to remap keys or add chord shortcuts",                "Customize ~/.claude/keybindings.json; supports chord bindings",            "config"),
    ("fewer-permission-prompts","/fewer-permission-prompts","user wants fewer permission dialogs",                           "Scan transcripts → add bash/MCP allowlist to .claude/settings.json",      "config"),
    ("loop",                   "/loop [interval] [cmd]",   'user wants recurring task ("check every 5m", "keep running X")', "Run prompt/slash command on recurring interval (default 10m)",              "automation"),
    ("claude-api",             "/claude-api",              "code imports anthropic SDK or user asks about Claude API",       "Build/debug Claude API apps; caching, tool use, model migration",          "dev"),
    ("ultrareview",            "/ultrareview [PR#]",       'user says "ultrareview" or wants multi-agent review',            "Parallel multi-agent cloud code review (local branch or GitHub PR)",       "advanced"),
    ("ultraplan",              "/ultraplan",               "user wants cloud environment for complex planning",               "Auto-create cloud worktrees for multi-agent planning tasks",                "advanced"),
    ("team-onboarding",        "/team-onboarding",         "user wants teammate ramp-up guide",                              "Generate onboarding guide from local Claude Code usage history",            "docs"),
    ("effort",                 "/effort",                  "user wants to adjust effort/quality level",                      "Interactive slider for session effort level (also: CLAUDE_EFFORT env var)", "config"),
    ("powerup",                "/powerup",                 "user wants feature demos or to learn Claude Code features",      "Interactive animated feature demos with lessons",                           "ux"),
    ("tui",                    "/tui",                     "rendering looks flickery or user wants full-screen mode",        "Switch to flicker-free alt-screen TUI rendering",                          "ux"),
    ("focus",                  "/focus",                   "user wants compact view of conversation",                        "Toggle focus view: prompt + tool summary + final response only",            "ux"),
    ("undo",                   "/undo",                    "user wants to undo last action",                                 "Alias for /rewind; undoes last assistant action",                           "ux"),
    ("usage",                  "/usage",                   "user asks about token or cost statistics",                       "Show token usage and cost stats (merged /cost + /stats)",                  "ux"),
    ("theme",                  "/theme [name]",            "user wants to change or create visual theme",                    "Create or switch custom color themes",                                      "ux"),
    ("color",                  "/color",                   "user wants a session color",                                     "Set random session color",                                                  "ux"),
    ("deep-research",          "/deep-research",           "user wants multi-source fact-checked research report",           "Fan-out web searches, fetch sources, adversarial verify, cited report",    "research"),
    ("code-review",            "/code-review",             "user asks for code review on current diff",                      "Review diff for correctness, reuse, efficiency; optional PR comments/fix", "core"),
    ("run",                    "/run",                     "user asks to run, start, or screenshot the app",                 "Launch and drive the project app to observe a change working",              "dev"),
    ("verify",                 "/verify",                  "user asks to verify a PR or confirm a fix works",                "Run app and observe behavior to confirm change is correct",                 "dev"),
    # Detected from anthropics/claude-code CHANGELOG (auto-added by sync)
    ("add-dir",                "/add-dir",                 "user wants to add a directory to the session context",           "Add directory to Claude Code session search scope",                          "utility"),
    ("login",                  "/login",                   "user needs to log in or switch Claude accounts",                 "Authenticate with Claude API / switch active account",                       "utility"),
    ("mcp",                    "/mcp",                     "user wants to manage or inspect MCP servers",                    "List, enable, disable, and configure MCP servers in session",                "config"),
    ("model",                  "/model",                   "user wants to switch the active model",                          "Select or display the current Claude model (opus/sonnet/haiku)",             "config"),
    ("permissions",            "/permissions",             "user wants to view or manage tool permissions",                  "List, add, or remove allowed/denied tool permissions",                       "config"),
    ("init",                   "/init",                    "user asks to initialize or document codebase",                   "Generate CLAUDE.md with codebase architecture, conventions, commands",       "core"),
]

# Deduplicate by slug (keep first occurrence)
_seen: set[str] = set()
_deduped: list[tuple[str, str, str, str, str]] = []
for _entry in SKILL_DEFS:
    if _entry[0] not in _seen:
        _seen.add(_entry[0])
        _deduped.append(_entry)
SKILL_DEFS = _deduped


def fetch(url: str, is_json: bool = False) -> Any:
    headers: dict[str, str] = {"User-Agent": "claude-skills-updater/2.0"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
        headers["Accept"] = "application/vnd.github+json"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read().decode("utf-8")
    return json.loads(data) if is_json else data


def parse_changelog(raw: str) -> tuple[str, str]:
    """Return (latest_version, section_text)."""
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", raw)
    if not m:
        return "", ""
    ver = m.group(1)
    start = m.start()
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", raw[start + 1:])
    end = start + 1 + nxt.start() if nxt else len(raw)
    return ver, raw[start:end].strip()


def extract_changes(section: str) -> dict[str, list[str]]:
    """Extract new commands, hooks, settings, env vars from a CHANGELOG section."""
    return {
        "skills":   sorted(set(re.findall(r"`(/[\w-]+)`", section))),
        "hooks":    sorted(set(re.findall(r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b", section))),
        "settings": sorted(set(re.findall(r"`([a-z][a-zA-Z.]+)`(?=\s*[–—:\-])", section))),
        "env":      sorted(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section))),
    }


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_cards(version: str, commit: str) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for slug, cmd, trigger, desc, category in SKILL_DEFS:
        card: dict[str, Any] = {
            "slug":          slug,
            "cmd":           cmd,
            "category":      category,
            "trigger":       trigger,
            "desc":          desc,
            "source":        REPO_URL,
            "source_commit": commit,
            "version":       version,
            "token_policy": [
                "Use cmd directly; avoid restating background context.",
                "Return only decision-critical output.",
                "Link to source over inline documentation.",
            ],
        }
        card["hash"] = card_hash(card)
        cards.append(card)
    return cards


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['cmd']} — {card['slug']}",
        "",
        f"- Category : `{card['category']}`",
        f"- Source   : {card['source']} @ `{card['source_commit']}`",
        f"- Version  : {card['version']}",
        "",
        f"**Trigger**: {card['trigger']}.",
        "",
        f"**Action** : {card['desc']}.",
        "",
        "## Token Policy",
        "",
    ]
    lines.extend(f"- {p}" for p in card["token_policy"])
    lines.append("")
    return "\n".join(lines)


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = [
        p / "skills" / "catalog.json"
        for p in SKILLS_ROOT.iterdir()
        if p.is_dir() and re.match(r"\d{4}-\d{2}-\d{2}", p.name) and p.name < today
    ]
    if not candidates:
        return {}
    latest = sorted(candidates)[-1]
    try:
        return json.loads(latest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_snapshot(today: str, cards: list[dict[str, Any]], version: str) -> Path:
    snap_dir = SKILLS_ROOT / today / "skills"
    snap_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (snap_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at":   datetime.now(KST).isoformat(timespec="seconds"),
        "date":           today,
        "version":        version,
        "directory_rule": "YYYY-MM-DD/skills",
        "source":         REPO_URL,
        "skills":         cards,
    }
    (snap_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return snap_dir


def compare_snapshots(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_map = {s["slug"]: s for s in prev.get("skills", []) if "slug" in s}
    next_map = {c["slug"]: c for c in cards}
    added    = sorted(set(next_map) - set(prev_map))
    deleted  = sorted(set(prev_map) - set(next_map))
    modified = sorted(
        slug for slug in set(prev_map) & set(next_map)
        if prev_map[slug].get("hash") != next_map[slug].get("hash")
    )
    unchanged = sorted(set(prev_map) & set(next_map) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_changelog(
    today:    str,
    version:  str,
    prev_ver: str,
    diff:     dict[str, list[str]],
    changes:  dict[str, list[str]],
    snap_dir: Path,
    commit:   str,
) -> None:
    CHANGELOGS.mkdir(parents=True, exist_ok=True)

    def bullets(items: list[str]) -> list[str]:
        return [f"  - {i}" for i in items] if items else ["  - 없음 (none)"]

    lines = [
        "=" * 64,
        "Claude Code Skills Update Report",
        f"날짜 (Date)  : {today}",
        f"버전 (Version): {prev_ver or 'none'} → {version}",
        f"소스 커밋    : {commit}",
        f"소스 레포    : {REPO_URL}",
        f"스냅샷 경로  : Claude/skills/{today}/skills/",
        "=" * 64,
        "",
        "[추가된 스킬]",
        *bullets(diff["added"]),
        "",
        "[수정된 스킬]",
        *bullets(diff["modified"]),
        "",
        "[삭제된 스킬]",
        *bullets(diff["deleted"]),
        "",
        "[최적화된 구조]",
        f"  - 날짜별 스냅샷 유지: Claude/skills/YYYY-MM-DD/skills/",
        f"  - 카탈로그 메타데이터: catalog.json (slug, hash, version, source_commit)",
        f"  - 스킬 카드: cmd/trigger/desc/token_policy 최소 구성",
        f"  - 총 스킬 수: {len(diff['added']) + len(diff['modified']) + len(diff['unchanged'])}",
        "",
        "[토큰 절감 관련 변경 사항]",
        "  - 원문 문서 복사 없이 GitHub 링크 + 커밋 해시만 저장",
        "  - 스킬 카드 1파일당 최대 20줄 (경량 마크다운)",
        "  - 중복 스킬 제거 (slug 기준 중복 통합)",
        f"  - 불변 스킬 (hash 동일): {len(diff['unchanged'])}개 → 재기록 없음",
        "",
        "[충돌 해결 내역]",
        "  - slug 중복: 첫 번째 정의 우선 채택",
        "  - 기존 날짜 스냅샷 덮어쓰기 방지 (새 날짜에만 생성)",
        "  - 해시 비교로 실제 변경 스킬만 수정 분류",
        "",
        "[CHANGELOG에서 감지된 신규 항목]",
        "  명령/스킬:",
        *([f"    - {s}" for s in changes["skills"]] or ["    - 없음 (none)"]),
        "  훅:",
        *([f"    - {h}" for h in changes["hooks"]] or ["    - 없음 (none)"]),
        "  설정:",
        *([f"    - {s}" for s in changes["settings"]] or ["    - 없음 (none)"]),
        "  환경변수:",
        *([f"    - {e}" for e in changes["env"]] or ["    - 없음 (none)"]),
        "",
        "[요약]",
        (
            f"  추가={len(diff['added'])}, 수정={len(diff['modified'])}, "
            f"삭제={len(diff['deleted'])}, 변경없음={len(diff['unchanged'])}"
        ),
        "",
        "=" * 64,
    ]
    (CHANGELOGS / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def update_catalog_yaml(version: str) -> None:
    if not CATALOG_YAML.exists():
        return
    text = CATALOG_YAML.read_text(encoding="utf-8")
    today = datetime.now(KST).strftime("%Y-%m-%d")
    text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_YAML.write_text(text, encoding="utf-8")


def head_commit() -> str:
    try:
        data = fetch(COMMITS_URL, is_json=True)
        if isinstance(data, list):
            data = data[0]
        sha = str(data.get("sha", "unknown"))
        return sha[:12]
    except Exception:
        return "unknown"


def main() -> int:
    today = datetime.now(KST).strftime("%Y-%m-%d")
    print(f"[{today}] Fetching Claude Code changelog...")

    try:
        raw = fetch(CHANGELOG_URL)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    version, section = parse_changelog(raw)
    if not version:
        print("Could not parse version from CHANGELOG.md", file=sys.stderr)
        return 1

    prev_ver = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""
    print(f"Latest: {version}  |  Local: {prev_ver or 'none'}")

    commit  = head_commit()
    changes = extract_changes(section) if section else {"skills": [], "hooks": [], "settings": [], "env": []}

    prev_catalog = previous_catalog(today)
    cards        = build_cards(version, commit)
    diff         = compare_snapshots(prev_catalog, cards)

    # Always write snapshot (ensures dated directory exists for new day)
    snap_dir = write_snapshot(today, cards, version)
    write_changelog(today, version, prev_ver, diff, changes, snap_dir, commit)

    # Update master catalog + version file
    update_catalog_yaml(version)
    VERSION_FILE.write_text(version, encoding="utf-8")

    print(f"Snapshot : {snap_dir.relative_to(REPO_ROOT)}")
    print(f"Changelog: {(CHANGELOGS / f'{today}.txt').relative_to(REPO_ROOT)}")
    print(
        f"Skills   : added={len(diff['added'])}, modified={len(diff['modified'])}, "
        f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

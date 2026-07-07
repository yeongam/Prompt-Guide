#!/usr/bin/env python3
"""Daily Claude Code skill sync from anthropics/claude-code CHANGELOG.md.

Fetches the official changelog, diffs against the last recorded version,
refreshes Claude/skills/SKILLS_CATALOG.yaml (+ .version), writes a dated
Claude/skills/{date}/skills snapshot, and records a compact changelog under
Claude/Changelogs/{date}.txt. Non-interactive, safe for daily cron/routine use.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_ROOT = REPO_ROOT / "Claude"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# Coding/programming/documentation-relevant commands worth first-class catalog
# entries when they first appear in the changelog backlog. Keyed by slash
# command name (without the leading slash).
TRACKED_COMMANDS: dict[str, dict[str, str]] = {
    "code-review": {
        "cmd": "/code-review <level> <pr#>",
        "trigger": "user wants multi-agent PR review at a chosen effort level",
        "desc": "Multi-agent review engine; /review stays a fast single-pass check; ultra level available",
    },
    "workflows": {
        "cmd": "/workflows",
        "trigger": "task needs orchestration across many agents (migrations, audits, broad sweeps)",
        "desc": "Dynamic workflows: Claude orchestrates tens-hundreds of agents in the background; view/manage runs here",
    },
    "dataviz": {
        "cmd": "/dataviz",
        "trigger": "user is building any chart, graph, dashboard, or plot",
        "desc": "Chart/dashboard design guidance with a runnable color-palette validator",
    },
    "deep-research": {
        "cmd": "/deep-research",
        "trigger": "user wants a deep, multi-source, fact-checked research report",
        "desc": "Fans out web search, fetches sources, adversarially verifies claims, synthesizes a cited report",
    },
    "goal": {
        "cmd": "/goal",
        "trigger": "user wants Claude to keep working across turns until a condition is met",
        "desc": "Set a completion condition; live elapsed/turns/tokens overlay; works interactive, -p, Remote Control",
    },
    "reload-skills": {
        "cmd": "/reload-skills",
        "trigger": "skill files changed on disk mid-session",
        "desc": "Re-scan skill directories without restarting the session",
    },
    "autofix-pr": {
        "cmd": "/autofix-pr",
        "trigger": "user wants failing PR checks diagnosed and fixed automatically",
        "desc": "Diagnoses and pushes fixes for failing CI checks on a PR",
    },
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_versions(changelog: str) -> list[tuple[str, str]]:
    """Return (version, section_text) pairs, newest first."""
    headers = list(re.finditer(r"^##\s+\[?(\d+\.\d+\.\d+)\]?.*$", changelog, re.MULTILINE))
    sections = []
    for i, m in enumerate(headers):
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(changelog)
        sections.append((m.group(1), changelog[start:end].strip()))
    return sections


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def new_sections_since(sections: list[tuple[str, str]], prev: str) -> list[tuple[str, str]]:
    if not prev:
        return sections[:1]
    out = []
    for ver, text in sections:
        if ver == prev:
            break
        out.append((ver, text))
    return out


def find_new_commands(combined_text: str) -> list[str]:
    mentioned = set(re.findall(r"`/([a-zA-Z][a-zA-Z-]*)", combined_text))
    return sorted(name for name in TRACKED_COMMANDS if name in mentioned)


def load_catalog_text() -> str:
    return CATALOG_FILE.read_text(encoding="utf-8") if CATALOG_FILE.exists() else ""


def catalog_has_skill(text: str, slug: str) -> bool:
    return bool(re.search(rf"^  {re.escape(slug)}:\s*$", text, re.MULTILINE))


def append_skill_entries(text: str, slugs: list[str]) -> tuple[str, list[str]]:
    added = [s for s in slugs if not catalog_has_skill(text, s)]
    if not added:
        return text, added
    block_lines = []
    for slug in added:
        info = TRACKED_COMMANDS[slug]
        block_lines.append(f"\n  {slug}:")
        block_lines.append(f"    cmd: {info['cmd']}")
        block_lines.append(f"    trigger: {info['trigger']}")
        block_lines.append(f"    desc: {info['desc']}")
    marker = "\n# ─── HOOKS "
    idx = text.find(marker)
    if idx == -1:
        return text + "\n".join(block_lines) + "\n", added
    return text[:idx] + "\n".join(block_lines) + "\n" + text[idx:], added


def update_models_block(text: str) -> tuple[str, bool]:
    new_block = (
        "models:\n"
        "  default: claude-sonnet-5\n"
        "  opus: claude-opus-4-8        # /effort xhigh available; fast mode 2x rate for 2.5x speed\n"
        "  sonnet: claude-sonnet-5      # native 1M-token context\n"
        "  haiku: claude-haiku-4-5-20251001\n"
        "  fable: claude-fable-5        # Mythos-class; gated by org Opus 4.8 enablement for auto-mode fallback\n"
    )
    pattern = re.compile(r"^models:\n(?:  .*\n)+", re.MULTILINE)
    if not pattern.search(text):
        return text, False
    replaced = pattern.sub(new_block, text, count=1)
    return replaced, replaced != text


def update_version_header(text: str, ver: str, date_str: str) -> str:
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {date_str}", text, flags=re.MULTILINE)
    return text


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def current_catalog_skills(text: str) -> list[dict[str, Any]]:
    """Parse the flat SKILLS_CATALOG.yaml skills: block into slug/cmd/trigger/desc cards."""
    m = re.search(r"^skills:\n(.*?)(?=^# ─── HOOKS|\Z)", text, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    body = m.group(1)
    cards = []
    for block in re.split(r"\n(?=  [a-zA-Z][\w-]*:\s*\n)", body):
        slug_m = re.match(r"\s*([a-zA-Z][\w-]*):\s*\n", block)
        if not slug_m:
            continue
        slug = slug_m.group(1)
        fields = dict(re.findall(r"^\s{4}(\w+):\s*(.*)$", block, re.MULTILINE))
        card = {"slug": slug, **fields}
        card["hash"] = card_hash(card)
        cards.append(card)
    return cards


def previous_dated_snapshot(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or not re.match(r"^\d{4}-\d{2}-\d{2}$", path.name) or path.name >= today:
            continue
        catalog = path / "skills" / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def skill_markdown(card: dict[str, Any]) -> str:
    return (
        f"# {card['slug']}\n\n"
        f"- Command: `{card.get('cmd', '')}`\n"
        f"- Trigger: {card.get('trigger', '')}\n"
        f"- Description: {card.get('desc', '')}\n"
    )


def write_dated_snapshot(today: str, cards: list[dict[str, Any]]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def diff_skills(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {c["slug"]: c for c in prev.get("skills", []) if "slug" in c}
    next_by_slug = {c["slug"]: c for c in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        s for s in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[s].get("hash") != next_by_slug[s].get("hash")
    )
    return {"added": added, "modified": modified, "deleted": deleted}


def write_changelog(
    today: str, prev_ver: str, new_ver: str, versions_covered: list[str],
    skill_diff: dict[str, list[str]], skills_dir: Path, is_baseline: bool,
) -> Path:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {v}" for v in values] if values else ["- 없음"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Source  : anthropics/claude-code CHANGELOG.md",
        f"Version : {prev_ver or 'none'} -> {new_ver}",
        f"Versions covered: {', '.join(versions_covered) if versions_covered else 'none'}",
        *(["", f"[참고] 첫 날짜 스냅샷 생성 - 신규 항목만 추가로 표기, 기존 스킬은 carry-over"] if is_baseline else []),
        "",
        "[추가된 스킬]",
        *bullets(skill_diff["added"]),
        "",
        "[수정된 스킬]",
        *bullets(skill_diff["modified"]),
        "",
        "[삭제된 스킬]",
        *bullets(skill_diff["deleted"]),
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(REPO_ROOT)}",
        "- 롤링 카탈로그(SKILLS_CATALOG.yaml)는 한 파일에서 cmd/trigger/desc만 유지",
        "- models 블록을 Sonnet 5 / Opus 4.8 / Haiku 4.5 / Fable 5 기준으로 갱신",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 원문 체인지로그 대신 커맨드/트리거/설명 3줄 카드로 압축",
        "- 날짜 스냅샷은 슬러그+해시 비교로만 diff, 원문 재저장 없음",
        "- 여러 버전(backlog)을 한 번에 병합 처리해 중복 changelog 엔트리 방지",
        "",
        "[충돌 해결 내역]",
        "- 슬러그 기준 중복 스킬은 기존 항목 유지, 신규만 추가",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에만 기록",
        "- ultrareview 등 기존 스킬은 삭제하지 않고 유지 (code-review가 상위 옵션 제공)",
        "",
    ]
    path = CHANGELOGS_ROOT / f"{today}.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    sections = parse_versions(changelog)
    if not sections:
        print("Could not parse any versions.", file=sys.stderr)
        return 1

    prev_ver = current_version()
    latest_ver = sections[0][0]
    print(f"Latest: {latest_ver}  |  Local: {prev_ver or 'none'}")

    if latest_ver == prev_ver:
        print("Already up to date. No changes.")
        return 0

    new_secs = new_sections_since(sections, prev_ver)
    versions_covered = [v for v, _ in new_secs]
    combined_text = "\n".join(t for _, t in new_secs)

    catalog_text = load_catalog_text()
    new_slugs = find_new_commands(combined_text)
    catalog_text, added_slugs = append_skill_entries(catalog_text, new_slugs)
    catalog_text, models_changed = update_models_block(catalog_text)
    catalog_text = update_version_header(catalog_text, latest_ver, today)
    CATALOG_FILE.write_text(catalog_text, encoding="utf-8")
    VERSION_FILE.write_text(latest_ver + "\n")

    cards = current_catalog_skills(catalog_text)
    prev_snapshot = previous_dated_snapshot(today)
    is_baseline = not prev_snapshot
    skills_dir = write_dated_snapshot(today, cards)
    skill_diff = diff_skills(prev_snapshot, cards)
    if is_baseline:
        skill_diff = {"added": added_slugs, "modified": [], "deleted": []}
    changelog_path = write_changelog(
        today, prev_ver, latest_ver, versions_covered, skill_diff, skills_dir, is_baseline
    )

    print(f"Updated: {prev_ver or 'none'} -> {latest_ver} ({len(versions_covered)} version(s) covered)")
    print(f"New skill entries added to catalog: {added_slugs or 'none'}")
    print(f"Models block changed: {models_changed}")
    print(f"Snapshot: {skills_dir.relative_to(REPO_ROOT)}")
    print(f"Changelog: {changelog_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

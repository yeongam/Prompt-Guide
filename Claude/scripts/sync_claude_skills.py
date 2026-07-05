#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code repository.

Dependency-free and non-interactive so it can run under cron or GitHub Actions.
Mirrors the GPT/scripts/sync_openai_skills.py pattern for this repo.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
REPO = "anthropics/claude-code"
BRANCH = "main"
CHANGELOG_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/CHANGELOG.md"
KST = timezone(timedelta(hours=9), "KST")


@dataclass(frozen=True)
class CoreSkill:
    slug: str
    name: str
    category: str  # coding | programming | documentation
    trigger: str
    output: str


# Curated coding/programming/documentation skills already tracked in SKILLS_CATALOG.yaml.
# Regenerated every run so their dated snapshot stays current with upstream commit state.
CORE_SKILLS: tuple[CoreSkill, ...] = (
    CoreSkill("init", "Init", "documentation",
              "user asks to initialize or document codebase",
              "CLAUDE.md with architecture, conventions, commands."),
    CoreSkill("review", "Review", "coding",
              "user asks to review a PR or branch",
              "Multi-pass review covering logic, style, security, tests."),
    CoreSkill("security-review", "Security Review", "coding",
              "user asks for a security audit of pending changes",
              "OWASP-focused, risk-ranked findings on the current diff."),
    CoreSkill("simplify", "Simplify", "coding",
              "user asks to clean up or refactor changed code",
              "Reuse/quality/efficiency pass on changed code, then fixes."),
    CoreSkill("session-start-hook", "Session Start Hook", "programming",
              "user wants test/lint runners on web session start",
              "SessionStart hook wiring for tests and linters."),
    CoreSkill("update-config", "Update Config", "programming",
              "automated behavior requests (hooks, permissions, env)",
              "settings.json changes for hooks, permissions, env vars."),
    CoreSkill("claude-api", "Claude API", "programming",
              "code imports the Claude/Anthropic SDK",
              "Build/debug Claude API usage: caching, tool use, model choice."),
)

CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "coding": ("code", "review", "refactor", "debug", "lint", "test"),
    "programming": ("sdk", "api", "hook", "plugin", "agent", "tool", "script", "build"),
    "documentation": ("doc", "readme", "changelog", "guide"),
}


def request_json(url: str) -> dict[str, Any]:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "prompt-guide-claude-skill-sync"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def repo_commit() -> str:
    try:
        data = request_json(f"https://api.github.com/repos/{REPO}/commits/{BRANCH}")
        return str(data.get("sha", ""))[:12] or "unknown"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return "unknown"


def fetch_changelog() -> str:
    try:
        return request_text(CHANGELOG_URL)
    except urllib.error.URLError:
        return ""


def latest_version_section(changelog: str) -> tuple[str, str]:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    if not m:
        return "", ""
    nxt = re.search(r"##\s+\[?\d+\.\d+\.\d+", changelog[m.end():])
    end = m.end() + nxt.start() if nxt else len(changelog)
    return m.group(1), changelog[m.start():end].strip()


def classify(text: str) -> str | None:
    lowered = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return category
    return None


def existing_catalog_slugs() -> set[str]:
    if not CATALOG_FILE.exists():
        return set()
    text = CATALOG_FILE.read_text(encoding="utf-8")
    body = text.split("# ─── HOOKS", 1)[0]
    return set(re.findall(r"^  ([a-zA-Z][\w-]*):$", body, flags=re.MULTILINE))


def discover_new_skills(section: str, known_slugs: set[str]) -> list[dict[str, Any]]:
    discovered: list[dict[str, Any]] = []
    seen_in_run: set[str] = set()
    for line in section.splitlines():
        for match in re.finditer(r"`(/[\w-]+)`", line):
            slug = match.group(1).lstrip("/")
            if slug in known_slugs or slug in seen_in_run:
                continue
            category = classify(line)
            if not category:
                continue
            discovered.append({"slug": slug, "line": line.strip(), "category": category})
            seen_in_run.add(slug)
    return discovered


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_core_card(skill: CoreSkill, commit: str) -> dict[str, Any]:
    card = {
        "name": skill.name,
        "slug": skill.slug,
        "category": skill.category,
        "source": f"https://github.com/{REPO}",
        "source_branch": BRANCH,
        "source_commit": commit,
        "trigger": skill.trigger,
        "procedure": [
            "Confirm the current SKILLS_CATALOG.yaml entry before acting.",
            "Prefer the smallest working change for the request.",
            "Reuse repo conventions instead of introducing new patterns.",
            "Keep prompts and tool calls short.",
            "Verify with the narrowest relevant check (test, lint, or diff review).",
        ],
        "output": skill.output,
        "token_policy": [
            "Reference SKILLS_CATALOG.yaml instead of restating its content.",
            "Return only decision-critical output.",
            "Avoid duplicating upstream documentation text.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Merge into SKILLS_CATALOG.yaml only when the slug is new or content changed.",
            "Preserve GPT and Gemini directories untouched.",
        ],
        "summary": skill.output,
    }
    card["hash"] = card_hash(card)
    return card


def build_discovered_card(item: dict[str, Any], commit: str) -> dict[str, Any]:
    slug = item["slug"]
    card = {
        "name": slug.replace("-", " ").title(),
        "slug": slug,
        "category": item["category"],
        "source": f"https://github.com/{REPO}",
        "source_branch": BRANCH,
        "source_commit": commit,
        "trigger": f"Introduced in the {REPO} changelog; confirm before relying on it.",
        "procedure": [
            "Confirm the command exists in the installed Claude Code version.",
            "Read the changelog entry for exact behavior.",
            "Adopt only if it fits an existing coding, programming, or documentation task.",
        ],
        "output": "New candidate skill pending catalog confirmation.",
        "token_policy": [
            "Keep the changelog excerpt as the only source text; do not expand it.",
        ],
        "compatibility": [
            "Do not remove an existing catalog entry that shares this slug.",
            "Record as a conflict instead of overwriting if the slug already exists.",
        ],
        "summary": item["line"][:280],
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Category: {card['category']}",
        f"- Source: {card['source']}",
        f"- Source commit: `{card['source_commit']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(card["procedure"], 1))
    lines.extend(["", "## Output", "", str(card["output"]), "", "## Token Policy", ""])
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines.extend(["", "## Compatibility", ""])
    lines.extend(f"- {item}" for item in card["compatibility"])
    lines.extend(["", "## Source Summary", "", str(card["summary"]), ""])
    return "\n".join(lines)


def current_date() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def previous_catalog(today: str) -> dict[str, Any]:
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
    latest = sorted(candidates)[-1]
    return json.loads(latest.read_text(encoding="utf-8"))


def write_dated_snapshot(today: str, cards: list[dict[str, Any]]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code repository only",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {item["slug"]: item for item in prev.get("skills", []) if "slug" in item}
    next_by_slug = {item["slug"]: item for item in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        slug for slug in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[slug].get("hash") != next_by_slug[slug].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def merge_into_catalog(discovered_cards: list[dict[str, Any]], version: str, today: str) -> list[str]:
    """Append genuinely new skills to SKILLS_CATALOG.yaml. Returns merged slugs."""
    if not CATALOG_FILE.exists() or not discovered_cards:
        return []
    text = CATALOG_FILE.read_text(encoding="utf-8")
    marker = "# ─── HOOKS"
    if marker not in text:
        return []
    head, tail = text.split(marker, 1)
    merged: list[str] = []
    for card in discovered_cards:
        entry = (
            f"\n  {card['slug']}:\n"
            f"    cmd: /{card['slug']}\n"
            f"    trigger: {card['trigger']}\n"
            f"    desc: {card['summary']}\n"
        )
        head += entry
        merged.append(card["slug"])
    if version:
        head = re.sub(r"^version:.*$", f"version: {version}", head, flags=re.MULTILINE)
    head = re.sub(r"^updated:.*$", f"updated: {today}", head, flags=re.MULTILINE)
    CATALOG_FILE.write_text(head + marker + tail, encoding="utf-8")
    return merged


def write_changelog(
    today: str,
    diff: dict[str, list[str]],
    merged_slugs: list[str],
    conflicts: list[str],
    skills_dir: Path,
    commit: str,
    version: str,
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {v}" for v in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: {skills_dir.relative_to(CLAUDE_ROOT)}",
        f"Source: {REPO}@{BRANCH} (commit {commit}, changelog version {version or 'unchanged'})",
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
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(CLAUDE_ROOT)}",
        "- SKILLS_CATALOG.yaml을 단일 참조본으로 유지, 스킬 카드는 요약만 보관",
        "- 각 스킬 카드는 trigger, procedure, output, token_policy, compatibility로 경량화",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 원문 CHANGELOG 복사 대신 커밋 해시와 요약 라인만 저장",
        "- 절차 항목은 5단계 이하로 제한, 중복 설명 제거",
        "- 카탈로그 병합 시 기존 설명을 덮어쓰지 않고 신규 슬러그만 추가",
        "",
        "[충돌 해결 내역]",
        *bullets(
            [f"신규 병합: {slug}" for slug in merged_slugs]
            + [f"슬러그 중복으로 병합 생략: {slug}" for slug in conflicts]
        ),
        "",
        "[요약]",
        (
            f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    today = current_date()
    commit = repo_commit()
    changelog = fetch_changelog()
    version, section = latest_version_section(changelog)

    known_slugs = existing_catalog_slugs()
    core_slugs = {skill.slug for skill in CORE_SKILLS}
    discovered_raw = discover_new_skills(section, known_slugs | core_slugs) if section else []

    cards = [build_core_card(skill, commit) for skill in CORE_SKILLS]
    discovered_cards = [build_discovered_card(item, commit) for item in discovered_raw]
    cards.extend(discovered_cards)

    prev = previous_catalog(today)
    diff = compare(prev, cards)

    skills_dir = write_dated_snapshot(today, cards)

    conflicts = [slug for slug in (c["slug"] for c in discovered_cards) if slug in known_slugs]
    to_merge = [c for c in discovered_cards if c["slug"] not in known_slugs]
    merged_slugs = merge_into_catalog(to_merge, version, today)
    if version:
        VERSION_FILE.write_text(version + "\n", encoding="utf-8")

    write_changelog(today, diff, merged_slugs, conflicts, skills_dir, commit, version)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Merged {len(merged_slugs)} new skill(s) into {CATALOG_FILE.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

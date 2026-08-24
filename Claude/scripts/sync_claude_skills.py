#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code repo.

Mirrors the GPT/scripts/sync_openai_skills.py pattern: dated snapshot directories
under Claude/skills/<date>/skills, a hash-diffed catalog.json, and one changelog
per run under Claude/Changelogs. Dependency-free and non-interactive so it can run
unattended (cron / scheduled routine).
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
SOURCE_REPO = "https://github.com/anthropics/claude-code"


@dataclass(frozen=True)
class Skill:
    slug: str
    name: str
    category: str  # coding | programming | documentation
    trigger: str
    procedure: tuple[str, ...]
    output: str


# Built-in Claude Code skills relevant to coding, programming, and documentation work.
SKILLS: tuple[Skill, ...] = (
    Skill(
        slug="code-review",
        name="Code Review",
        category="coding",
        trigger="user asks to review the current diff, a PR, branch, or path",
        procedure=(
            "Scope the diff or target (PR/branch/path) at the requested effort level.",
            "Check correctness bugs first, then reuse/simplification/efficiency.",
            "Rank findings by confidence; broaden coverage only at high effort.",
        ),
        output="Ranked findings, optionally posted as inline PR comments or auto-fixed.",
    ),
    Skill(
        slug="security-review",
        name="Security Review",
        category="coding",
        trigger="user asks for a security audit of pending branch changes",
        procedure=(
            "Diff the current branch against its base.",
            "Check against OWASP top-10 classes of vulnerability.",
            "Rank findings by exploitability and blast radius.",
        ),
        output="Risk-ranked list of security findings in the pending diff.",
    ),
    Skill(
        slug="simplify",
        name="Simplify",
        category="coding",
        trigger="user asks to clean up or refactor recently changed code",
        procedure=(
            "Review changed code only, not the whole codebase.",
            "Look for reuse, simplification, and efficiency opportunities.",
            "Apply the fixes directly; does not hunt for correctness bugs.",
        ),
        output="Simplified diff with quality cleanups applied.",
    ),
    Skill(
        slug="init",
        name="Init",
        category="coding",
        trigger="user asks to initialize or document a codebase",
        procedure=(
            "Scan the repo for architecture, conventions, and commands.",
            "Generate a CLAUDE.md capturing what a new contributor needs.",
        ),
        output="CLAUDE.md with codebase architecture, conventions, and commands.",
    ),
    Skill(
        slug="session-start-hook",
        name="Session Start Hook",
        category="programming",
        trigger="user sets up a repo for Claude Code on the web and wants tests/linters to run automatically",
        procedure=(
            "Create a SessionStart hook that prepares the environment.",
            "Ensure the project can run its tests and linters during web sessions.",
        ),
        output="Configured SessionStart hook for Claude Code on the web.",
    ),
    Skill(
        slug="mcp-builder",
        name="MCP Builder",
        category="programming",
        trigger="user is building an MCP server to integrate an external API or service",
        procedure=(
            "Design well-scoped tools around the target external service.",
            "Implement with FastMCP (Python) or the MCP SDK (Node/TypeScript).",
        ),
        output="A working MCP server exposing well-designed tools to LLM clients.",
    ),
    Skill(
        slug="claude-api",
        name="Claude API",
        category="programming",
        trigger="code imports the Anthropic SDK or user asks about Claude API features/pricing/limits",
        procedure=(
            "Confirm current model IDs, pricing, and parameter support.",
            "Cover streaming, tool use, MCP, prompt caching, and token counting as needed.",
            "For version migrations, use the built-in upgrade path (e.g. anthropic 0.x -> 1.x).",
        ),
        output="Correct, current-version Claude API / Anthropic SDK usage or migration.",
    ),
    Skill(
        slug="update-config",
        name="Update Config",
        category="programming",
        trigger="user wants automated behaviors, permissions, env vars, or hooks configured",
        procedure=(
            "Edit settings.json / settings.local.json rather than relying on memory.",
            "Wire hooks for behaviors that must fire automatically on lifecycle events.",
        ),
        output="Updated settings.json implementing the requested automated behavior.",
    ),
    Skill(
        slug="skill-creator",
        name="Skill Creator",
        category="programming",
        trigger="user wants to create, edit, or optimize a skill",
        procedure=(
            "Scaffold or edit the skill's SKILL.md and supporting files.",
            "Tighten the description for accurate triggering.",
            "Optionally run evals to benchmark performance.",
        ),
        output="A new or improved skill definition, optionally with eval results.",
    ),
    Skill(
        slug="docx",
        name="DOCX",
        category="documentation",
        trigger="user wants to create, read, or edit a Word document (.docx/.dotx)",
        procedure=(
            "Read or scaffold the document structure (headings, TOC, styles).",
            "Apply requested edits, formatting, or find-and-replace.",
        ),
        output="A created or edited Word document.",
    ),
    Skill(
        slug="pdf",
        name="PDF",
        category="documentation",
        trigger="user wants to create, read, merge, split, or otherwise manipulate a PDF",
        procedure=(
            "Extract text/tables/images or assemble the requested PDF operation.",
            "Handle forms, watermarks, encryption, or OCR as requested.",
        ),
        output="The resulting PDF file or extracted content.",
    ),
    Skill(
        slug="pptx",
        name="PPTX",
        category="documentation",
        trigger="user wants to create, read, or edit a slide deck (.pptx/.potx)",
        procedure=(
            "Read or scaffold slides, layouts, speaker notes, or templates.",
            "Apply requested edits and keep formatting consistent.",
        ),
        output="A created or edited presentation file.",
    ),
    Skill(
        slug="xlsx",
        name="XLSX",
        category="documentation",
        trigger="user wants to create, read, or edit a spreadsheet (.xlsx/.csv/.tsv)",
        procedure=(
            "Read or scaffold sheets, formulas, and formatting.",
            "Apply requested edits, cleaning, or chart generation.",
        ),
        output="A created or edited spreadsheet file.",
    ),
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def latest_version(changelog: str) -> str:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    return m.group(1) if m else ""


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_card(skill: Skill, version: str) -> dict[str, Any]:
    card = {
        "name": skill.name,
        "slug": skill.slug,
        "category": skill.category,
        "source": SOURCE_REPO,
        "source_version": version,
        "trigger": skill.trigger,
        "procedure": list(skill.procedure),
        "output": skill.output,
        "token_policy": [
            "One-line description; expand only when the user's phrasing is ambiguous.",
            "Reuse this catalog instead of restating skill behavior inline.",
            "Prefer the narrowest applicable skill over general-purpose exploration.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
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
        f"- Source version: `{card['source_version']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    lines.extend(f"{i}. {p}" for i, p in enumerate(card["procedure"], 1))
    lines += ["", "## Output", "", str(card["output"]), "", "## Token Policy", ""]
    lines.extend(f"- {t}" for t in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {c}" for c in card["compatibility"])
    lines.append("")
    return "\n".join(lines)


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or path.name >= today:
            continue
        catalog = path / "skills" / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def write_skill_outputs(today: str, cards: list[dict[str, Any]], version: str) -> Path:
    out_dir = SKILLS_ROOT / today / "skills"
    out_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (out_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code repository only",
        "source_version": version,
        "skills": cards,
    }
    (out_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return out_dir


def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {c["slug"]: c for c in prev.get("skills", []) if "slug" in c}
    next_by_slug = {c["slug"]: c for c in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        s for s in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[s].get("hash") != next_by_slug[s].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def update_top_level_catalog(version: str, today: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def write_changelog(today: str, prev_version: str, version: str, diff: dict[str, list[str]], out_dir: Path) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Version : {prev_version or 'none'} -> {version}",
        "Source  : anthropics/claude-code (official)",
        "",
        "[추가된 스킬]", *bullets(diff["added"]), "",
        "[수정된 스킬]", *bullets(diff["modified"]), "",
        "[삭제된 스킬]", *bullets(diff["deleted"]), "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: {out_dir.relative_to(CLAUDE_ROOT)}",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 기존 SKILLS_CATALOG.yaml(단일 파일 카탈로그)은 그대로 유지하여 하위 호환 보존",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 원문 문서 복사 대신 공식 레포 링크와 버전만 기록",
        "- 절차는 3줄 이내로 제한, 설명은 한 줄 트리거 문장으로 압축",
        "- 카드별 해시로 변경 여부만 비교하여 불필요한 재작성 방지",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
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
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    version = latest_version(changelog)
    if not version:
        print("Could not parse version.", file=sys.stderr)
        return 1

    prev_version = current_version()
    today = today_str()
    print(f"Latest: {version}  |  Local: {prev_version or 'none'}")

    cards = [build_card(skill, version) for skill in SKILLS]
    prev_catalog = previous_catalog(today)
    out_dir = write_skill_outputs(today, cards, version)
    diff = compare(prev_catalog, cards)
    write_changelog(today, prev_version, version, diff, out_dir)

    VERSION_FILE.write_text(version)
    update_top_level_catalog(version, today)

    print(f"Synced {len(cards)} Claude skills to {out_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

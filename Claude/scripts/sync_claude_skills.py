#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code repo.

Mirrors GPT/scripts/sync_openai_skills.py: dependency-free and non-interactive so it
can run unattended (daily routine / GitHub Actions) without prompts. Scope is limited
to bundled skills relevant to coding, programming, and documentation work.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
KST = timezone(timedelta(hours=9), "KST")

REPO = "anthropics/claude-code"
BRANCH = "main"
CHANGELOG_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/CHANGELOG.md"


@dataclass(frozen=True)
class SkillSource:
    slug: str
    name: str
    trigger: str
    procedure: tuple[str, ...]
    output: str
    removed: bool = False


# Scope: bundled skills tied to coding, programming, or documentation work only.
# (config/UX-only skills like keybindings-help or loop are intentionally excluded)
SOURCES: tuple[SkillSource, ...] = (
    SkillSource(
        slug="init",
        name="Init",
        trigger="user asks to initialize or document a codebase",
        procedure=(
            "Scan repo structure, build tooling, and conventions.",
            "Generate CLAUDE.md with architecture and commands.",
        ),
        output="CLAUDE.md documenting the codebase for future sessions.",
    ),
    SkillSource(
        slug="code-review",
        name="Code Review",
        trigger="review a diff, PR number, branch, or path for bugs and cleanup",
        procedure=(
            "Renamed from /review; reports correctness bugs at a chosen effort level.",
            "Also surfaces reuse/simplification/efficiency cleanups.",
            "--comment posts inline PR comments; --fix applies findings to the working tree.",
        ),
        output="Ranked findings, optionally posted as PR comments or auto-fixed.",
    ),
    SkillSource(
        slug="simplify",
        name="Simplify",
        trigger="user asks to clean up or refactor already-changed code",
        procedure=(
            "Cleanup-only pass: reuse, simplification, efficiency, altitude.",
            "Applies fixes directly; does not hunt for correctness bugs (use code-review).",
        ),
        output="Working tree with cleanup fixes applied.",
    ),
    SkillSource(
        slug="security-review",
        name="Security Review",
        trigger="user asks for a security audit of pending branch changes",
        procedure=(
            "OWASP-focused audit of the pending diff.",
            "Outputs risk-ranked findings.",
        ),
        output="Risk-ranked security findings for the current diff.",
    ),
    SkillSource(
        slug="session-start-hook",
        name="Session Start Hook",
        trigger="user wants test/lint runners available in web Claude Code sessions",
        procedure=(
            "Create a SessionStart hook so the project can run tests and linters.",
        ),
        output="Configured SessionStart hook in the repo.",
    ),
    SkillSource(
        slug="claude-api",
        name="Claude API",
        trigger="code imports the anthropic SDK, or user asks about Claude API features",
        procedure=(
            "Context cost cut from ~200k+ to ~25k tokens via on-demand reference docs.",
            "`upgrade` subcommand migrates Python projects from anthropic 0.x to 1.x.",
            "`prompt-audit` subcommand audits prompts/tool descriptions for stale patterns.",
            "Covers Admin API (members, invites, workspaces, keys, rate limits, CMEK).",
        ),
        output="API/SDK guidance, migration steps, or a prompt audit report.",
    ),
    SkillSource(
        slug="workflow-authoring",
        name="Workflow Authoring",
        trigger="authoring a Workflow tool script the user already opted into",
        procedure=(
            "Split out of the Workflow tool description to cut its footprint from ~5.7k to ~1k tokens.",
            "Covers script API, gotchas, resume, and quality patterns.",
        ),
        output="A workflow script following the documented API and patterns.",
    ),
    SkillSource(
        slug="dataviz",
        name="Dataviz",
        trigger="creating any chart, graph, plot, or dashboard in any output medium",
        procedure=(
            "Apply the brand-neutral palette and form heuristics before writing chart code.",
            "Validate colors with the runnable OKLab color-difference palette validator.",
        ),
        output="A chart/dashboard consistent in light and dark, with accessible colors.",
    ),
    SkillSource(
        slug="artifact-design",
        name="Artifact Design",
        trigger="load before writing any HTML/Markdown artifact",
        procedure=(
            "Apply design fundamentals before the first line of an artifact.",
            "Applies even to skill-instructed Markdown artifacts.",
        ),
        output="An artifact that follows the design system's fundamentals.",
    ),
    SkillSource(
        slug="artifact-capabilities",
        name="Artifact Capabilities",
        trigger="an artifact needs runtime behavior (live data, saved state, per-viewer memory)",
        procedure=(
            "Load before declaring `capabilities` or writing `window.claude.*` runtime code.",
        ),
        output="An artifact wired to the correct runtime capability contract.",
    ),
    SkillSource(
        slug="artifact-diagramming",
        name="Artifact Diagramming",
        trigger="a diagram would clarify an artifact's mechanism",
        procedure=(
            "Draw the real mechanism, not decoration.",
            "Use inline-SVG mechanics that stay legible in both themes.",
        ),
        output="A legible inline-SVG diagram inside the artifact.",
    ),
    SkillSource(
        slug="run",
        name="Run",
        trigger="user asks to run, start, or screenshot the app to confirm a change works",
        procedure=(
            "Prefer a project skill that already covers launching the app.",
            "Otherwise fall back to built-in patterns per project type.",
        ),
        output="The app running with the change verified live, not just by tests.",
    ),
    SkillSource(
        slug="skill-doctor",
        name="Skill Doctor",
        trigger="user wants to see which loaded skills go unused and their context cost",
        procedure=(
            "Added as `/skill-doctor`.",
            "Reports unused loaded skills and their token cost so they can be pruned.",
        ),
        output="A report of loaded-skill usage and context cost.",
    ),
    SkillSource(
        slug="ultraplan",
        name="Ultraplan (removed)",
        trigger="n/a",
        procedure=("Feature removed from Claude Code; kept here only as a tombstone.",),
        output="n/a",
        removed=True,
    ),
)


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def repo_reference(version: str) -> str:
    # api.github.com is scoped to this session's own repo only, so external repos
    # can't resolve a commit sha here; the CHANGELOG version tag is the reference.
    return f"v{version}" if version else "unknown"


def latest_version(changelog: str) -> str:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    return m.group(1) if m else ""


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_card(source: SkillSource, commit: str, version: str) -> dict[str, Any]:
    card = {
        "name": source.name,
        "slug": source.slug,
        "source": f"https://github.com/{REPO}",
        "source_branch": BRANCH,
        "source_commit": commit,
        "source_version": version,
        "removed": source.removed,
        "trigger": source.trigger,
        "procedure": list(source.procedure),
        "output": source.output,
        "token_policy": [
            "Avoid repeated background context.",
            "Return only decision-critical instructions.",
            "Link to the official repo instead of copying long docs.",
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
        f"- Source: {card['source']} @ `{card['source_commit']}`",
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
    lines.append("")
    return "\n".join(lines)


def current_date() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


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


def write_outputs(today: str, cards: list[dict[str, Any]]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code repository only",
        "scope": "coding, programming, and documentation-related bundled skills",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    dupes: set[str] = set()
    for card in cards:
        slug = str(card.get("slug", ""))
        (dupes if slug in seen else seen).add(slug)
    if dupes:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(dupes))}")


def compare(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {item["slug"]: item for item in prev.get("skills", []) if "slug" in item}
    next_by_slug = {item["slug"]: item for item in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        s for s in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[s].get("hash") != next_by_slug[s].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def update_legacy_catalog(version: str, today: str) -> None:
    """Keep the legacy non-dated SKILLS_CATALOG.yaml version/date fields in sync."""
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text(encoding="utf-8")
    text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text, encoding="utf-8")
    VERSION_FILE.write_text(version + "\n", encoding="utf-8")


def write_changelog(
    today: str,
    prev_version: str,
    version: str,
    diff: dict[str, list[str]],
    skills_dir: Path,
    notes: list[str],
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Source: anthropics/claude-code ({prev_version or 'none'} -> {version})",
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
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 레거시 SKILLS_CATALOG.yaml은 버전/날짜 필드만 동기화, 본문은 날짜별 스냅샷이 단일 소스",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 CHANGELOG 복사를 피하고 공식 레포 링크와 커밋 해시만 저장",
        "- 스킬 절차는 검증된 변경 사항 기준 짧은 항목으로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스킬 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "- 레거시 scripts/update_skills.py(및 changelogs/ 경로)는 별도 대상이라 충돌 없음; 본 스크립트가 Claude/Changelogs 표준 경로 담당",
        *notes,
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
    try:
        changelog = request_text(CHANGELOG_URL)
        version = latest_version(changelog)
        commit = repo_reference(version)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    prev_version = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""

    cards = [build_card(s, commit, version) for s in SOURCES]
    ensure_unique(cards)

    prev_catalog = previous_catalog(today)
    skills_dir = write_outputs(today, cards)
    diff = compare(prev_catalog, cards)

    notes = []
    if not prev_catalog:
        notes.append(
            "- 최초 날짜별 스냅샷 생성: 레거시 단일 SKILLS_CATALOG.yaml(v"
            f"{prev_version or 'unknown'})을 GPT와 동일한 날짜별 구조로 이전"
        )

    write_changelog(today, prev_version, version, diff, skills_dir, notes)
    update_legacy_catalog(version, today)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    print(f"Version: {prev_version or 'none'} -> {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

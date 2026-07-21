#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code repo.

Mirrors the dated-snapshot pattern used by GPT/scripts/sync_openai_skills.py:
writes Claude/skills/<date>/skills/*.md + catalog.json, diffs against the most
recent prior snapshot, and appends one changelog to Claude/Changelogs/<date>.txt.
Dependency-free and non-interactive so it can run unattended on a schedule.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1] / "Claude"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CATALOG_FILE = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
VERSION_FILE = SKILLS_ROOT / ".version"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
UTC = timezone.utc


@dataclass(frozen=True)
class Skill:
    slug: str
    name: str
    cmd: str
    trigger: str
    procedure: tuple[str, ...]
    output: str
    summary: str
    status: str  # "added" | "modified" relative to the flat catalog this repo already had


# Curated set: coding / programming / documentation-relevant skills confirmed present
# in the official CHANGELOG.md but missing (or stale) in this repo's flat catalog.
SKILLS: tuple[Skill, ...] = (
    Skill(
        slug="code-review",
        name="Code Review",
        cmd="/code-review",
        trigger="user wants a correctness/bug pass over pending changes, at a chosen effort level",
        procedure=(
            "Diff the pending changes against the base ref.",
            "Run the bug-hunting review at the requested effort level.",
            "Rank findings by severity; verify each before reporting.",
            "With --comment, post findings as inline GitHub PR comments.",
        ),
        output="Severity-ranked correctness findings for the current diff.",
        summary="Renamed from /simplify; now reports correctness bugs at a chosen effort "
        "level (e.g. `/code-review high`). /review <pr> reuses this engine for a fast "
        "single-pass PR review.",
        status="added",
    ),
    Skill(
        slug="verify",
        name="Verify",
        cmd="/verify",
        trigger="user wants a specific claim, fix, or finding independently checked",
        procedure=(
            "Restate the claim to verify.",
            "Check it against the actual code/state, not prior assumptions.",
            "Report CONFIRMED or REFUTED with the concrete evidence.",
        ),
        output="A confirm/refute verdict with supporting evidence.",
        summary="No longer auto-invoked; run explicitly with /verify when a claim or fix "
        "needs independent confirmation.",
        status="added",
    ),
    Skill(
        slug="debug",
        name="Debug",
        cmd="/debug",
        trigger="user asks Claude to help troubleshoot the current session",
        procedure=(
            "Toggle debug logging on for the session.",
            "Reproduce the issue and capture relevant logs.",
            "Summarize the likely cause with log evidence.",
        ),
        output="Debug logging enabled plus a session-issue diagnosis.",
        summary="Debug logs are no longer written by default; /debug toggles them on mid-session.",
        status="added",
    ),
    Skill(
        slug="dataviz",
        name="Dataviz",
        cmd="/dataviz",
        trigger="user is about to create any chart, graph, plot, or dashboard",
        procedure=(
            "Pick a chart form matching the data shape.",
            "Apply the validated default palette (perceptual OKLab-checked).",
            "Style for both light and dark themes.",
        ),
        output="Chart/dashboard code following the bundled color and layout guidance.",
        summary="Bundled skill for chart/dashboard design guidance with a runnable "
        "color-palette validator; palette and color-blindness thresholds are recalibrated "
        "in current releases.",
        status="added",
    ),
    Skill(
        slug="workflows",
        name="Workflows",
        cmd="/workflows",
        trigger="user explicitly asks for multi-agent orchestration of a task",
        procedure=(
            "Confirm explicit user opt-in before spawning a fleet.",
            "Script the phases: fan-out, verify, synthesize.",
            "Track live runs and progress via /workflows.",
        ),
        output="A background multi-agent run orchestrating tens to hundreds of agents.",
        summary="Dynamic workflows orchestrate work across many agents in the background "
        "for larger, more complex tasks; /workflows views current runs.",
        status="added",
    ),
    Skill(
        slug="commit-push-pr",
        name="Commit Push PR",
        cmd="/commit-push-pr",
        trigger="user wants to commit, push, and open a PR in one step",
        procedure=(
            "Stage the relevant files and write a descriptive commit message.",
            "Push to the configured push remote (falls back to origin).",
            "Open the PR and post its URL wherever configured (e.g. Slack via MCP).",
        ),
        output="A pushed commit and an opened pull request.",
        summary="Auto-allows push to remote.pushDefault (or the sole remote) in addition "
        "to origin, and can post PR URLs to configured Slack channels.",
        status="added",
    ),
    Skill(
        slug="autofix-pr",
        name="Autofix PR",
        cmd="/autofix-pr",
        trigger="user wants CI failures or review comments on an open PR fixed automatically",
        procedure=(
            "Read failing checks / review comments on the target PR.",
            "Diagnose and push a fix commit.",
            "Re-check CI status after pushing.",
        ),
        output="A fix pushed to the PR branch, or a diagnosis if out of scope.",
        summary="Works from a git worktree or another repository without the earlier "
        "'cannot run on the default branch' false rejection.",
        status="added",
    ),
    Skill(
        slug="pr-comments",
        name="PR Comments",
        cmd="/pr-comments",
        trigger="user wants outstanding review comments on a PR triaged or answered",
        procedure=(
            "Fetch open review comments on the PR.",
            "Address or reply to each with enough context to stand alone.",
            "Skip duplicates or already-resolved threads silently.",
        ),
        output="Replies or fixes for outstanding PR review comments.",
        status="added",
        summary="Reads and responds to pull request review comments; recent releases "
        "fixed the model selection used for this command.",
    ),
)

_HASH_FIELDS = ("slug", "name", "cmd", "trigger", "procedure", "output", "summary")


def card_hash(skill: Skill) -> str:
    payload = {k: getattr(skill, k) for k in _HASH_FIELDS}
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def fetch_changelog() -> str:
    req = urllib.request.Request(CHANGELOG_SRC, headers={"User-Agent": "claude-skills-sync/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def latest_version(changelog: str) -> str:
    m = re.search(r"^##\s+\[?(\d+\.\d+\.\d+)\]?", changelog, flags=re.MULTILINE)
    return m.group(1) if m else ""


def current_date() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def skill_markdown(skill: Skill, version: str) -> str:
    lines = [
        f"# {skill.name}",
        "",
        f"- Slug: `{skill.slug}`",
        f"- Command: `{skill.cmd}`",
        f"- Source: https://github.com/anthropics/claude-code",
        f"- Source version: `{version}`",
        f"- Trigger: {skill.trigger}",
        "",
        "## Procedure",
        "",
    ]
    lines.extend(f"{i}. {step}" for i, step in enumerate(skill.procedure, 1))
    lines += [
        "",
        "## Output",
        "",
        skill.output,
        "",
        "## Token Policy",
        "",
        "- Avoid repeated background context; return only decision-critical output.",
        "- Link to the official repo instead of copying changelog prose.",
        "",
        "## Compatibility",
        "",
        "- Do not overwrite existing dated skill snapshots.",
        "- Integrate into Claude/skills/SKILLS_CATALOG.yaml only if slug is new or hash changed.",
        "- Preserve changelog evidence for every generated update.",
        "",
        "## Source Summary",
        "",
        skill.summary,
        "",
    ]
    return "\n".join(lines)


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


def write_snapshot(today: str, version: str) -> tuple[Path, list[dict[str, Any]]]:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    cards = []
    for skill in SKILLS:
        (skills_dir / f"{skill.slug}.md").write_text(skill_markdown(skill, version), encoding="utf-8")
        cards.append(
            {
                "slug": skill.slug,
                "name": skill.name,
                "cmd": skill.cmd,
                "hash": card_hash(skill),
            }
        )

    catalog = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code repository only",
        "source_version": version,
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir, cards


def diff_catalog(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {c["slug"]: c for c in prev.get("skills", [])}
    next_by_slug = {c["slug"]: c for c in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        s for s in set(prev_by_slug) & set(next_by_slug) if prev_by_slug[s]["hash"] != next_by_slug[s]["hash"]
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def update_flat_catalog(version: str, today: str, diff: dict[str, list[str]]) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)

    if diff["added"]:
        by_slug = {s.slug: s for s in SKILLS}
        block_lines = []
        for slug in diff["added"]:
            s = by_slug[slug]
            block_lines += [
                f"  {s.slug}:",
                f"    cmd: {s.cmd}",
                f"    trigger: {s.trigger}",
                f"    desc: {s.output}",
                "",
            ]
        insertion = "\n".join(block_lines)
        # Insert before the HOOKS section marker so new entries stay nested
        # under the top-level `skills:` mapping instead of dangling at EOF.
        marker = "# ─── HOOKS "
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx] + insertion + text[idx:]
        else:
            text = text.rstrip("\n") + "\n\n" + insertion.rstrip("\n") + "\n"

    if "simplify" in diff.get("modified", []) or "code-review" in diff["added"]:
        text = re.sub(
            r"(simplify:\n\s+cmd: /simplify\n\s+trigger:.*\n\s+desc: ).*",
            r"\1Cleanup-only review (reuse/simplification/efficiency/altitude); "
            r"use /code-review for correctness bugs",
            text,
        )

    CATALOG_FILE.write_text(text)


def write_changelog(today: str, version: str, prev_version: str, diff: dict[str, list[str]], skills_dir: Path) -> Path:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {v}" for v in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Version : {prev_version or 'none'} -> {version}",
        "Source  : https://github.com/anthropics/claude-code",
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
        f"- 날짜별 스냅샷 구조 도입: {skills_dir.relative_to(CLAUDE_ROOT)} (Claude/skills/YYYY-MM-DD/skills)",
        "- 기존 SKILLS_CATALOG.yaml은 유지하고 신규/변경 항목만 반영 (하위 호환)",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 원문 CHANGELOG 전체 복사 대신 커맨드별 핵심 요약만 저장",
        "- 공식 레포 링크와 버전만 기록, 반복 배경 설명 생략",
        "- 변경 감지는 hash 비교로 수행하여 불필요한 재작성 방지",
        "",
        "[충돌 해결 내역]",
        "- /simplify 는 cleanup-only 로 범위 축소, 신규 /code-review 가 정확성 버그 리뷰 담당 (레포 결정 반영)",
        "- slug 기준으로 신규 스킬만 추가, 기존 SKILLS_CATALOG.yaml 항목은 덮어쓰지 않음",
        "- 날짜 스냅샷은 과거 날짜 디렉토리를 덮어쓰지 않고 신규 날짜에만 기록",
        "",
        "[요약]",
        (
            f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
    ]
    path = CHANGELOGS_ROOT / f"{today}.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch_changelog()
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    version = latest_version(changelog)
    if not version:
        print("Could not parse version.", file=sys.stderr)
        return 1
    prev_version = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""
    today = current_date()

    prev_catalog = previous_catalog(today)
    skills_dir, cards = write_snapshot(today, version)
    diff = diff_catalog(prev_catalog, cards)
    update_flat_catalog(version, today, diff)
    VERSION_FILE.write_text(version)
    changelog_path = write_changelog(today, version, prev_version, diff, skills_dir)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Version: {prev_version or 'none'} -> {version}")
    print(f"Changelog: {changelog_path.relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

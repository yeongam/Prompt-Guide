#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code repository.

Dependency-free and non-interactive so it can run in GitHub Actions without prompts.
Mirrors the pattern established by GPT/scripts/sync_openai_skills.py.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import textwrap
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
SOURCE_REPO = "anthropics/claude-code"
SOURCE_BRANCH = "main"
UTC = timezone.utc


@dataclass(frozen=True)
class SourceSkill:
    slug: str
    name: str
    cmd: str
    trigger: str
    procedure: tuple[str, ...]
    output: str


# Coding, programming, and documentation-relevant skills only (per routine scope).
# UI/cosmetic toggles (theme, color, focus, tui, undo, usage) are tracked in
# SKILLS_CATALOG.yaml but not expanded into dated cards here.
SOURCES: tuple[SourceSkill, ...] = (
    SourceSkill(
        slug="init",
        name="Init",
        cmd="/init",
        trigger="user asks to initialize or document the codebase",
        procedure=(
            "Scan repo structure, build/test/lint commands, and conventions.",
            "Draft CLAUDE.md sections: overview, commands, architecture, style.",
            "Keep instructions terse and actionable, no filler prose.",
        ),
        output="CLAUDE.md capturing architecture, conventions, and commands.",
    ),
    SourceSkill(
        slug="code-review",
        name="Code Review",
        cmd="/review",
        trigger="user asks to review a PR, branch, or diff",
        procedure=(
            "Diff the target branch/PR against its base.",
            "Check logic correctness, style consistency, security, and test coverage.",
            "Rank findings by severity; verify before reporting.",
        ),
        output="Multi-pass review report with severity-ranked, verified findings.",
    ),
    SourceSkill(
        slug="security-review",
        name="Security Review",
        cmd="/security-review",
        trigger="user asks for a security audit of pending changes",
        procedure=(
            "Diff the current branch against its base.",
            "Audit for OWASP Top 10 classes (injection, XSS, auth, secrets).",
            "Rank findings by exploitability and impact.",
        ),
        output="Risk-ranked security findings for the pending diff.",
    ),
    SourceSkill(
        slug="simplify",
        name="Simplify",
        cmd="/simplify",
        trigger="user asks to clean up or refactor changed code",
        procedure=(
            "Review only the changed code, not the whole file.",
            "Flag reuse, simplification, and efficiency opportunities.",
            "Apply the fixes directly; leave bug-hunting to code-review.",
        ),
        output="Simplified diff with quality fixes applied.",
    ),
    SourceSkill(
        slug="session-start-hook",
        name="Session Start Hook",
        cmd="/session-start-hook",
        trigger="user wants test/lint runners available on web session start",
        procedure=(
            "Detect the project's test and lint commands.",
            "Create a SessionStart hook in settings.json running them.",
            "Verify the hook fires without interactive prompts.",
        ),
        output="SessionStart hook ensuring tests/linters are ready in web sessions.",
    ),
    SourceSkill(
        slug="update-config",
        name="Update Config",
        cmd="/update-config",
        trigger='automated behavior requests ("when X", "allow Y", "set Z=val")',
        procedure=(
            "Identify whether the request needs a hook, permission, or env var.",
            "Edit settings.json (project or user scope) accordingly.",
            "Confirm the change matches the requested trigger condition.",
        ),
        output="settings.json updated with the requested hook/permission/env var.",
    ),
    SourceSkill(
        slug="claude-api",
        name="Claude API",
        cmd="/claude-api",
        trigger="code imports the Anthropic SDK; user asks about Claude API features",
        procedure=(
            "Confirm current model IDs and API surface before coding.",
            "Apply prompt caching, tool use, or migration guidance as needed.",
            "Verify against the Anthropic SDK reference, not memory.",
        ),
        output="Working Claude API integration aligned with current SDK behavior.",
    ),
    SourceSkill(
        slug="team-onboarding",
        name="Team Onboarding",
        cmd="/team-onboarding",
        trigger="user wants a teammate ramp-up guide",
        procedure=(
            "Pull local Claude Code usage history and repo conventions.",
            "Summarize common workflows, commands, and gotchas.",
            "Produce a concise onboarding guide, not a full manual.",
        ),
        output="Onboarding guide generated from local usage history and repo docs.",
    ),
    SourceSkill(
        slug="fewer-permission-prompts",
        name="Fewer Permission Prompts",
        cmd="/fewer-permission-prompts",
        trigger="user wants fewer permission dialogs",
        procedure=(
            "Scan session transcripts for repeated read-only Bash/MCP calls.",
            "Propose a prioritized allowlist.",
            "Write the allowlist to project .claude/settings.json.",
        ),
        output="Allowlist added to settings.json reducing repeat permission prompts.",
    ),
    SourceSkill(
        slug="loop",
        name="Loop",
        cmd="/loop [interval] [/command]",
        trigger='user wants a recurring task ("check every 5m", "keep running X")',
        procedure=(
            "Parse the interval and target prompt/command.",
            "Schedule repeated firing at that interval, self-pacing if omitted.",
            "Stop cleanly when the user ends the loop.",
        ),
        output="Recurring execution of the given prompt/command at the set interval.",
    ),
)

TOKEN_POLICY: tuple[str, ...] = (
    "Avoid repeated background context across turns.",
    "Return only decision-critical instructions or code.",
    "Link to the official repo instead of copying long docs.",
)

COMPATIBILITY: tuple[str, ...] = (
    "Do not overwrite existing dated skill snapshots.",
    "Integrate only if slug is unique or content hash changed.",
    "Preserve GPT/Gemini directory behavior; do not modify them.",
)


def request_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def repo_commit(repo: str, branch: str) -> str:
    """Resolve the latest commit via git smart-HTTP (works without a scoped API token)."""
    out = subprocess.run(
        ["git", "ls-remote", f"https://github.com/{repo}.git", branch],
        capture_output=True, text=True, timeout=30, check=True,
    ).stdout
    sha = out.split()[0] if out.strip() else ""
    return sha[:12]


def repo_changelog() -> str:
    try:
        return request_text(f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_BRANCH}/CHANGELOG.md")
    except urllib.error.URLError:
        return ""


def parse_latest_version(changelog: str) -> str:
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    return m.group(1) if m else ""


def compact_text(text: str, max_chars: int = 420) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "."


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill(source: SourceSkill, commit: str, version: str, latest_section: str) -> dict[str, Any]:
    card = {
        "name": source.name,
        "slug": source.slug,
        "cmd": source.cmd,
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_branch": SOURCE_BRANCH,
        "source_commit": commit,
        "source_version": version,
        "trigger": source.trigger,
        "procedure": list(source.procedure),
        "output": source.output,
        "token_policy": list(TOKEN_POLICY),
        "compatibility": list(COMPATIBILITY),
        "summary": compact_text(latest_section) or f"Claude Code {version}",
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Command: `{card['cmd']}`",
        f"- Source: {card['source']}",
        f"- Source commit: `{card['source_commit']}` (v{card['source_version']})",
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
    lines.extend(["", "## Source Summary", "", textwrap.fill(str(card["summary"]), width=88), ""])
    return "\n".join(lines)


def current_date() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.name) or path.name >= today:
            continue
        catalog = path / "skills" / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    latest = sorted(candidates)[-1]
    return json.loads(latest.read_text(encoding="utf-8"))


def write_skill_outputs(today: str, cards: list[dict[str, Any]], commit: str, version: str) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")

    catalog = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "source_commit": commit,
        "source_version": version,
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    return skills_dir


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for card in cards:
        slug = str(card.get("slug", ""))
        if slug in seen:
            duplicates.add(slug)
        seen.add(slug)
    if duplicates:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(duplicates))}")


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


def update_catalog_version(version: str, today: str) -> None:
    if not CATALOG_FILE.exists() or not version:
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)
    VERSION_FILE.write_text(version + "\n")


def write_changelog(today: str, diff: dict[str, list[str]], skills_dir: Path, commit: str, version: str) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: {skills_dir.relative_to(CLAUDE_ROOT.parent)}",
        f"Source: {SOURCE_REPO}@{SOURCE_BRANCH} ({commit}, v{version})",
        "",
        "[추가된 스킬]", *bullets(diff["added"]), "",
        "[수정된 스킬]", *bullets(diff["modified"]), "",
        "[삭제된 스킬]", *bullets(diff["deleted"]), "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: Claude/skills/{today}/skills",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- SKILLS_CATALOG.yaml은 단일 파일 요약본으로 유지 (버전/갱신일 동기화)",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 CHANGELOG 복사를 피하고 커밋 해시와 버전만 저장",
        "- 스킬 절차는 3단계 내외의 짧은 실행 단위로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스킬 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "- 죽은 브랜치(claude/zealous-sagan-FdaL5, claude/kind-feynman-XQCh2)를 참조하던"
        " 구버전 scripts/update_skills.py, scripts/sync_changelogs.sh,"
        " scripts/setup_local_cron.sh, .github/workflows/daily-skill-update.yml을"
        " 제거하고 GPT/ 루틴과 동일한 패턴(Claude/scripts, Claude/Changelogs,"
        " Claude-scoped workflow)으로 대체",
        "",
        "[요약]",
        (
            "- skills: "
            f"added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    today = current_date()

    commit = repo_commit(SOURCE_REPO, SOURCE_BRANCH)
    changelog = repo_changelog()
    version = parse_latest_version(changelog) or "unknown"
    latest_section = changelog.split("\n## ", 2)[1] if "\n## " in changelog else changelog

    cards = [build_skill(source, commit, version, latest_section) for source in SOURCES]
    ensure_unique(cards)

    prev = previous_catalog(today)
    skills_dir = write_skill_outputs(today, cards, commit, version)
    diff = compare(prev, cards)
    update_catalog_version(version, today)
    write_changelog(today, diff, skills_dir, commit, version)

    print(f"Synced {len(cards)} Claude Code skills to {skills_dir.relative_to(CLAUDE_ROOT.parent)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Sync compact Claude Code skill and hook cards from the official Anthropic
claude-code repository into dated snapshots (mirrors GPT/scripts/sync_openai_skills.py).

Dependency-free and non-interactive so it can run from an unattended routine.
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
HOOKS_ROOT = CLAUDE_ROOT / "hooks"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
SOURCE_REPO = "https://github.com/anthropics/claude-code"
KST = timezone(timedelta(hours=9), "KST")


@dataclass(frozen=True)
class SkillSource:
    slug: str
    name: str
    cmd: str
    trigger: str
    procedure: tuple[str, ...]
    output: str


@dataclass(frozen=True)
class HookSource:
    slug: str
    name: str
    event: str
    trigger: str
    checks: tuple[str, ...]
    actions: tuple[str, ...]


# Curated from Claude/skills/SKILLS_CATALOG.yaml: coding, programming, and
# documentation-focused skills only (per routine scope).
SKILLS: tuple[SkillSource, ...] = (
    SkillSource(
        slug="claude-code-init-documentation",
        name="Codebase Init Documentation",
        cmd="/init",
        trigger="User asks to initialize or document a codebase.",
        procedure=(
            "Scan repo structure, build system, and conventions.",
            "Generate CLAUDE.md with architecture and commands.",
            "Keep entries factual; avoid speculative guidance.",
        ),
        output="CLAUDE.md covering architecture, conventions, and commands.",
    ),
    SkillSource(
        slug="pr-review-programming",
        name="PR & Branch Review",
        cmd="/review",
        trigger="User asks to review a PR or branch.",
        procedure=(
            "Multi-pass check: logic, style, security, tests.",
            "Rank findings by severity before reporting.",
        ),
        output="Ranked review findings for the diff under review.",
    ),
    SkillSource(
        slug="security-review-programming",
        name="Security Review",
        cmd="/security-review",
        trigger="User asks for a security audit of pending changes.",
        procedure=(
            "OWASP-focused audit of the current branch diff.",
            "Rank risk by exploitability and blast radius.",
        ),
        output="Risk-ranked security findings for pending diffs.",
    ),
    SkillSource(
        slug="code-simplify-refactor",
        name="Code Simplify & Refactor",
        cmd="/simplify",
        trigger="User asks to clean up or refactor changed code.",
        procedure=(
            "Review changed code for reuse, quality, efficiency.",
            "Apply fixes directly; skip bug-hunting (use /review).",
        ),
        output="Simplified diff with reuse/efficiency issues fixed.",
    ),
    SkillSource(
        slug="claude-api-sdk-programming",
        name="Claude API SDK Programming",
        cmd="/claude-api",
        trigger="Code imports the Anthropic SDK or user asks about Claude API features.",
        procedure=(
            "Check model IDs and current SDK request shapes.",
            "Apply prompt caching and tool-use patterns correctly.",
            "Flag deprecated model IDs during migration.",
        ),
        output="Working Claude API integration or migration fix.",
    ),
    SkillSource(
        slug="session-hooks-programming",
        name="Session Hooks Programming",
        cmd="/session-start-hook",
        trigger="User wants test/lint runners on session start (web Claude Code).",
        procedure=(
            "Create a SessionStart hook in .claude/settings.json.",
            "Verify the hook runs project test/lint commands.",
        ),
        output="SessionStart hook wired to project test/lint commands.",
    ),
    SkillSource(
        slug="settings-hooks-config",
        name="Settings & Hooks Configuration",
        cmd="/update-config",
        trigger='Automated-behavior requests ("when X", "allow Y", "set Z=val").',
        procedure=(
            "Edit settings.json for hooks, permissions, or env vars.",
            "Prefer narrow permission scopes over broad allowlists.",
        ),
        output="settings.json updated with the requested hook/permission/env change.",
    ),
    SkillSource(
        slug="team-onboarding-documentation",
        name="Team Onboarding Documentation",
        cmd="/team-onboarding",
        trigger="User wants a teammate ramp-up guide.",
        procedure=(
            "Read local Claude Code usage history and data.",
            "Generate an onboarding guide from observed patterns.",
        ),
        output="Onboarding guide generated from local usage history.",
    ),
)

# Curated from the hooks section of SKILLS_CATALOG.yaml.
HOOKS: tuple[HookSource, ...] = (
    HookSource(
        slug="pre-tool-use-guard",
        name="Pre Tool Use Guard",
        event="PreToolUse",
        trigger="Fires before any tool execution.",
        checks=("Validate or log the pending bash/file operation.",),
        actions=("Block with exit 2 or {decision:\"block\"}; inject context if needed.",),
    ),
    HookSource(
        slug="post-tool-use-logger",
        name="Post Tool Use Logger",
        event="PostToolUse",
        trigger="Fires after a tool call completes.",
        checks=("Confirm the tool result matches expected shape.",),
        actions=("Log results; trigger follow-up actions.",),
    ),
    HookSource(
        slug="pre-compact-guard",
        name="Pre Compact Guard",
        event="PreCompact",
        trigger="Fires before conversation compaction (added v2.1.85).",
        checks=("Check whether a critical operation is mid-flight.",),
        actions=("Block compaction via exit 2 or {decision:\"block\"} until safe.",),
    ),
    HookSource(
        slug="task-created-tracker",
        name="Task Created Tracker",
        event="TaskCreated",
        trigger="Fires when a task is created via TaskCreate (added v2.1.90).",
        checks=("Confirm task metadata is complete before logging.",),
        actions=("Log/track task creation events.",),
    ),
    HookSource(
        slug="worktree-create-provisioner",
        name="Worktree Create Provisioner",
        event="WorktreeCreate",
        trigger="Fires on worktree creation (added v2.1.88).",
        checks=("Verify the HTTP endpoint returns a valid worktreePath.",),
        actions=("Provision the worktree via the configured HTTP endpoint.",),
    ),
    HookSource(
        slug="permission-denied-escalation",
        name="Permission Denied Escalation",
        event="PermissionDenied",
        trigger="Fires after an auto-mode classifier denial (added v2.1.95).",
        checks=("Confirm escalation criteria before requesting a retry.",),
        actions=('Return {"retry": true} to re-run the classifier when appropriate.',),
    ),
)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def source_version() -> str:
    try:
        changelog = fetch_text(CHANGELOG_SRC)
    except urllib.error.URLError:
        return "unknown"
    m = re.search(r"##\s+\[?(\d+\.\d+\.\d+)\]?", changelog)
    return m.group(1) if m else "unknown"


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill(source: SkillSource, version: str) -> dict[str, Any]:
    card = {
        "name": source.name,
        "slug": source.slug,
        "cmd": source.cmd,
        "source": SOURCE_REPO,
        "source_version": version,
        "trigger": source.trigger,
        "procedure": list(source.procedure),
        "output": source.output,
        "token_policy": [
            "Avoid repeated background context; use the catalog entry instead.",
            "Return only decision-critical code or instructions.",
            "Link to the source repo instead of copying long docs.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve SKILLS_CATALOG.yaml as the flat canonical reference.",
        ],
    }
    card["hash"] = card_hash(card)
    return card


def build_hook(source: HookSource, version: str) -> dict[str, Any]:
    card = {
        "name": source.name,
        "slug": source.slug,
        "event": source.event,
        "source": SOURCE_REPO,
        "source_version": version,
        "trigger": source.trigger,
        "checks": list(source.checks),
        "actions": list(source.actions),
        "token_policy": [
            "Keep hook cards short enough for quick pre/post-run loading.",
            "Prefer catalog metadata over repeated inline context.",
        ],
        "compatibility": [
            "Do not modify GPT or Gemini directories.",
            "Do not overwrite existing dated hook snapshots.",
        ],
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Command: `{card['cmd']}`",
        f"- Source: {card['source']} (v{card['source_version']})",
        f"- Trigger: {card['trigger']}",
        "",
        "## Procedure",
        "",
    ]
    lines.extend(f"{i}. {p}" for i, p in enumerate(card["procedure"], 1))
    lines += ["", "## Output", "", str(card["output"]), "", "## Token Policy", ""]
    lines.extend(f"- {p}" for p in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {p}" for p in card["compatibility"])
    return "\n".join(lines) + "\n"


def hook_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Slug: `{card['slug']}`",
        f"- Event: `{card['event']}`",
        f"- Source: {card['source']} (v{card['source_version']})",
        f"- Trigger: {card['trigger']}",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"{i}. {c}" for i, c in enumerate(card["checks"], 1))
    lines += ["", "## Actions", ""]
    lines.extend(f"- {a}" for a in card["actions"])
    lines += ["", "## Token Policy", ""]
    lines.extend(f"- {p}" for p in card["token_policy"])
    lines += ["", "## Compatibility", ""]
    lines.extend(f"- {p}" for p in card["compatibility"])
    return "\n".join(lines) + "\n"


def current_date() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def previous_catalog(root: Path, today: str, leaf_dir: str) -> dict[str, Any]:
    if not root.exists():
        return {}
    candidates = []
    for path in root.iterdir():
        if not path.is_dir() or path.name >= today:
            continue
        catalog = path / leaf_dir / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    latest = sorted(candidates)[-1]
    return json.loads(latest.read_text(encoding="utf-8"))


def write_skill_outputs(today: str, cards: list[dict[str, Any]]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official Anthropic claude-code GitHub repository only",
        "scope": "coding, programming, documentation skills only",
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def write_hook_outputs(today: str, cards: list[dict[str, Any]]) -> Path:
    hooks_dir = HOOKS_ROOT / today / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (hooks_dir / f"{card['slug']}.md").write_text(hook_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/hooks",
        "source_policy": "official Anthropic claude-code GitHub repository only",
        "hooks": cards,
    }
    (hooks_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return hooks_dir


def compare(prev: dict[str, Any], cards: list[dict[str, Any]], collection: str) -> dict[str, list[str]]:
    prev_by_slug = {item["slug"]: item for item in prev.get(collection, []) if "slug" in item}
    next_by_slug = {item["slug"]: item for item in cards}
    added = sorted(set(next_by_slug) - set(prev_by_slug))
    deleted = sorted(set(prev_by_slug) - set(next_by_slug))
    modified = sorted(
        slug for slug in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[slug].get("hash") != next_by_slug[slug].get("hash")
    )
    unchanged = sorted(set(prev_by_slug) & set(next_by_slug) - set(modified))
    return {"added": added, "modified": modified, "deleted": deleted, "unchanged": unchanged}


def write_changelog(
    today: str,
    version: str,
    skill_diff: dict[str, list[str]],
    hook_diff: dict[str, list[str]],
    skills_dir: Path,
    hooks_dir: Path,
    changelog_dir_created: bool,
) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills and Hooks Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Hooks: Claude/hooks/{today}/hooks",
        f"Source: {SOURCE_REPO} (v{version})",
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
        "[추가된 훅]",
        *bullets(hook_diff["added"]),
        "",
        "[수정된 훅]",
        *bullets(hook_diff["modified"]),
        "",
        "[삭제된 훅]",
        *bullets(hook_diff["deleted"]),
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: {skills_dir.relative_to(CLAUDE_ROOT)}",
        f"- 날짜별 훅 스냅샷 구조 유지: {hooks_dir.relative_to(CLAUDE_ROOT)}",
        "- 각 스킬은 trigger, procedure, output, token_policy, compatibility로 경량화",
        "- 각 훅은 event, checks, actions, token_policy, compatibility로 경량화",
        "- SKILLS_CATALOG.yaml(플랫 카탈로그)은 그대로 유지, 날짜별 스냅샷과 병행",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 긴 원문 문서 복사를 피하고 공식 레포 링크와 버전만 저장",
        "- 스킬 절차와 훅 점검 항목은 짧은 실행 단위로 제한",
        "- 중복 설명 대신 공통 catalog.json으로 메타데이터 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬/훅 통합",
        "- 기존 SKILLS_CATALOG.yaml, .version, update_skills.py는 변경 없이 유지 (하위 호환)",
        f"- Changelogs 디렉토리 {'신규 생성' if changelog_dir_created else '기존 유지 (중복 생성 없음)'}",
        "- 변경 감지는 hash 비교로 수행",
        "",
        "[요약]",
        (
            "- skills: "
            f"added={len(skill_diff['added'])}, modified={len(skill_diff['modified'])}, "
            f"deleted={len(skill_diff['deleted'])}, unchanged={len(skill_diff['unchanged'])}"
        ),
        (
            "- hooks: "
            f"added={len(hook_diff['added'])}, modified={len(hook_diff['modified'])}, "
            f"deleted={len(hook_diff['deleted'])}, unchanged={len(hook_diff['unchanged'])}"
        ),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def ensure_unique(cards: list[dict[str, Any]], label: str) -> None:
    seen: set[str] = set()
    dupes: set[str] = set()
    for card in cards:
        slug = str(card.get("slug", ""))
        if slug in seen:
            dupes.add(slug)
        seen.add(slug)
    if dupes:
        raise ValueError(f"Duplicate {label} slugs: {', '.join(sorted(dupes))}")


def main() -> int:
    today = current_date()
    version = source_version()
    changelog_dir_created = not CHANGELOGS_ROOT.exists()

    skills = [build_skill(s, version) for s in SKILLS]
    hooks = [build_hook(h, version) for h in HOOKS]
    ensure_unique(skills, "skill")
    ensure_unique(hooks, "hook")

    prev_skills = previous_catalog(SKILLS_ROOT, today, "skills")
    prev_hooks = previous_catalog(HOOKS_ROOT, today, "hooks")

    skills_dir = write_skill_outputs(today, skills)
    hooks_dir = write_hook_outputs(today, hooks)

    skill_diff = compare(prev_skills, skills, "skills")
    hook_diff = compare(prev_hooks, hooks, "hooks")
    write_changelog(today, version, skill_diff, hook_diff, skills_dir, hooks_dir, changelog_dir_created)

    print(f"Synced {len(skills)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Synced {len(hooks)} Claude hooks to {hooks_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

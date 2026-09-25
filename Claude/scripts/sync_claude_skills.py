#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from the official anthropics/claude-code repo.

Mirrors GPT/scripts/sync_openai_skills.py: dated snapshots under
Claude/skills/YYYY-MM-DD/skills/, a diff against the previous snapshot, and a
changelog under Claude/Changelogs/YYYY-MM-DD.txt. Dependency-free and
non-interactive so it can run in GitHub Actions or an unattended session.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import urllib.error
import urllib.request

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
LEGACY_CATALOG = SKILLS_ROOT / "SKILLS_CATALOG.yaml"
LEGACY_VERSION_FILE = SKILLS_ROOT / ".version"
SOURCE_REPO = "anthropics/claude-code"
CHANGELOG_URL = f"https://raw.githubusercontent.com/{SOURCE_REPO}/main/CHANGELOG.md"


@dataclass(frozen=True)
class SkillSource:
    slug: str
    cmd: str
    trigger: str
    desc: str
    procedure: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)


# Official, coding/programming/documentation-relevant skills confirmed against
# the live anthropics/claude-code skill set and CHANGELOG.md mentions.
SOURCES: tuple[SkillSource, ...] = (
    SkillSource("init", "/init", "user asks to initialize or document codebase",
                "Generate CLAUDE.md with codebase architecture, conventions, commands"),
    SkillSource("code-review", "/code-review", "user asks to review a diff, PR, branch, or path",
                "Multi-pass review for correctness bugs plus reuse/simplification/efficiency cleanups"),
    SkillSource("security-review", "/security-review", "user asks security audit of current branch changes",
                "OWASP-focused audit of pending diffs; outputs risk-ranked findings"),
    SkillSource("simplify", "/simplify", "user asks to clean up or refactor changed code",
                "Review changed code for reuse/quality/efficiency, then fix issues"),
    SkillSource("session-start-hook", "/session-start-hook",
                "user wants test/lint runners on session start (web Claude Code)",
                "Create SessionStart hook ensuring project can run tests and linters"),
    SkillSource("update-config", "/update-config", "automated behavior requests (\"when X\", \"allow Y\", \"set Z=val\")",
                "Configure settings.json; handles hooks, permissions, env vars"),
    SkillSource("keybindings-help", "/keybindings-help", "user wants to remap keys or add chord shortcuts",
                "Customize keybindings.json; supports chord bindings"),
    SkillSource("fewer-permission-prompts", "/fewer-permission-prompts", "user wants fewer permission dialogs",
                "Scan transcripts, add bash/MCP allowlist to .claude/settings.json"),
    SkillSource("loop", "/loop [interval] [/command]",
                "user wants a recurring task (e.g. \"check every 5m\", \"keep running X\")",
                "Run a prompt or slash command on a recurring interval (self-paced if no interval)"),
    SkillSource("claude-api", "/claude-api", "code imports the Anthropic SDK; user asks about Claude API features",
                "Build/debug Claude API apps: prompt caching, tool use, model migration",
                extra={"models": {"opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5",
                                   "haiku": "claude-haiku-4-5-20251001"}}),
    SkillSource("workflow-authoring", "/workflow-authoring (reference)",
                "authoring a multi-agent Workflow tool script the user opted into",
                "Script API, resume semantics, and worked examples for Workflow scripts"),
    SkillSource("run", "/run", "user asks to run, start, or screenshot the app to verify a change",
                "Launch and drive the project app; falls back to built-in patterns per project type"),
    SkillSource("dataviz", "(auto-trigger: chart/graph/plot/dashboard)",
                "about to create any chart, graph, plot, or data visualization",
                "Design-system-agnostic chart/color/layout guidance for artifacts and code"),
    SkillSource("artifact-design", "(auto-trigger: before writing any artifact)",
                "writing any Artifact, including a skill-instructed Markdown one",
                "Design fundamentals and contract for Artifacts (fonts, theming, size limits)"),
    SkillSource("artifact-diagramming", "(auto-trigger: artifact needs a diagram)",
                "a picture would clarify an artifact's mechanism",
                "Inline-SVG diagramming mechanics that stay legible in both themes"),
    SkillSource("artifact-capabilities", "(auto-trigger: artifact needs runtime behavior)",
                "an artifact needs live data, shared state, or another runtime capability",
                "Runtime capability roster and typed call definitions for published Artifacts"),
    SkillSource("ultrareview", "/ultrareview [PR#]", "user says \"ultrareview\" or wants multi-agent review",
                "Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR"),
    SkillSource("ultraplan", "/ultraplan", "user wants a cloud environment for complex planning",
                "Auto-create cloud worktrees/environments for multi-agent planning tasks"),
    SkillSource("team-onboarding", "/team-onboarding", "user wants a teammate ramp-up guide",
                "Generate onboarding guide from local Claude Code usage history/data"),
    SkillSource("effort", "/effort", "user wants to adjust effort/quality level",
                "Interactive slider for session effort level (also: CLAUDE_EFFORT env var)"),
    SkillSource("powerup", "/powerup", "user wants feature demos or to learn Claude Code features",
                "Interactive animated feature demos with lessons"),
    SkillSource("tui", "/tui", "rendering looks flickery or user wants full-screen mode",
                "Switch to flicker-free alt-screen TUI rendering"),
    SkillSource("focus", "/focus", "user wants a compact view of the conversation",
                "Toggle focus view showing only: prompt + tool summary + final response"),
)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_latest_version(changelog: str) -> str:
    m = re.search(r"^##\s+\[?(\d+\.\d+\.\d+)\]?", changelog, flags=re.MULTILINE)
    return m.group(1) if m else "unknown"


def fetch_commit_sha(repo: str) -> str:
    """Best-effort; returns '' when the GitHub API isn't reachable (e.g. scoped sandbox)."""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "prompt-guide-claude-skill-sync"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/commits/main", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
        return str(data.get("sha", ""))[:12]
    except (urllib.error.URLError, ValueError, OSError):
        return ""


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_card(source: SkillSource, version: str, commit: str) -> dict[str, Any]:
    card = {
        "slug": source.slug,
        "cmd": source.cmd,
        "source": f"https://github.com/{SOURCE_REPO}",
        "source_version": version,
        "source_commit": commit,
        "trigger": source.trigger,
        "desc": source.desc,
        "token_policy": [
            "Keep card to trigger + one-line desc; no upstream doc copies.",
            "Link to the official repo instead of inlining long guidance.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
        ],
    }
    if source.extra:
        card.update(source.extra)
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['slug']}",
        "",
        f"- Cmd: `{card['cmd']}`",
        f"- Source: {card['source']} @ {card['source_version']}"
        + (f" ({card['source_commit']})" if card["source_commit"] else ""),
        f"- Trigger: {card['trigger']}",
        "",
        "## Desc",
        "",
        card["desc"],
        "",
        "## Token Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in card["token_policy"])
    lines.extend(["", "## Compatibility", ""])
    lines.extend(f"- {item}" for item in card["compatibility"])
    if "models" in card:
        lines.extend(["", "## Models", ""])
        lines.extend(f"- {k}: `{v}`" for k, v in card["models"].items())
    return "\n".join(lines) + "\n"


def current_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def previous_snapshot(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = []
    for path in SKILLS_ROOT.iterdir():
        if not path.is_dir() or path.name >= today:
            continue
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", path.name):
            continue
        catalog = path / "skills" / "catalog.json"
        if catalog.exists():
            candidates.append(catalog)
    if not candidates:
        return {}
    return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))


def write_snapshot(today: str, cards: list[dict[str, Any]], version: str) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code repository only",
        "source_version": version,
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return skills_dir


def diff_cards(prev: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
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


def update_legacy_catalog(version: str, today: str) -> None:
    """Keep the flat SKILLS_CATALOG.yaml / .version in sync for existing readers."""
    if LEGACY_VERSION_FILE.exists() or LEGACY_CATALOG.exists():
        LEGACY_VERSION_FILE.write_text(version + "\n", encoding="utf-8")
        if LEGACY_CATALOG.exists():
            text = LEGACY_CATALOG.read_text(encoding="utf-8")
            text = re.sub(r"^version:.*$", f"version: {version}", text, flags=re.MULTILINE)
            text = re.sub(r"^updated:.*$", f"updated: {today}", text, flags=re.MULTILINE)
            LEGACY_CATALOG.write_text(text, encoding="utf-8")


def write_changelog(today: str, diff: dict[str, list[str]], version: str, skills_dir: Path) -> None:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- 없음 (none)"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Source: {SOURCE_REPO} (CHANGELOG.md @ {version})",
        "",
        "[추가된 스킬 / Added]",
        *bullets(diff["added"]),
        "",
        "[수정된 스킬 / Modified]",
        *bullets(diff["modified"]),
        "",
        "[삭제된 스킬 / Deleted]",
        *bullets(diff["deleted"]),
        "",
        "[최적화된 구조 / Structure optimizations]",
        f"- 날짜별 스냅샷 구조 적용: {skills_dir.relative_to(CLAUDE_ROOT)} (GPT 루틴과 동일한 YYYY-MM-DD/skills 규칙)",
        "- 각 스킬은 cmd, trigger, desc, token_policy, compatibility로 경량화",
        "- 기존 SKILLS_CATALOG.yaml / .version은 하위 호환을 위해 유지·동기화",
        "",
        "[토큰 절감 관련 변경 사항 / Token savings]",
        "- 스킬 카드는 trigger + 한 줄 설명만 유지, 원문 changelog 텍스트는 복사하지 않음",
        "- 공통 메타데이터(catalog.json)로 통합, 카드별 중복 설명 제거",
        "- 변경 감지는 hash 비교로 수행하여 불필요한 재작성을 피함",
        "",
        "[충돌 해결 내역 / Conflict resolution]",
        "- 'review' 슬러그를 실제 공식 스킬명인 'code-review'로 통합 (중복/구식 명칭 제거)",
        "- slug 기준 중복 스킬 통합, 기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- claude-api 카드의 모델 ID를 현재 유효한 모델로 갱신 (기존 기능 손상 없음)",
        "",
        "[요약 / Summary]",
        (
            f"- added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
    ]
    (CHANGELOGS_ROOT / f"{today}.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch_text(CHANGELOG_URL)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    version = fetch_latest_version(changelog)
    commit = fetch_commit_sha(SOURCE_REPO)
    today = current_date()

    cards = [build_card(s, version, commit) for s in SOURCES]
    slugs = [c["slug"] for c in cards]
    if len(slugs) != len(set(slugs)):
        dupes = {s for s in slugs if slugs.count(s) > 1}
        raise ValueError(f"Duplicate skill slugs: {sorted(dupes)}")

    prev = previous_snapshot(today)
    skills_dir = write_snapshot(today, cards, version)
    diff = diff_cards(prev, cards)
    write_changelog(today, diff, version, skills_dir)
    update_legacy_catalog(version, today)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT)}")
    print(f"Changelog: {(CHANGELOGS_ROOT / f'{today}.txt').relative_to(CLAUDE_ROOT)}")
    print(f"Diff: +{len(diff['added'])} ~{len(diff['modified'])} -{len(diff['deleted'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

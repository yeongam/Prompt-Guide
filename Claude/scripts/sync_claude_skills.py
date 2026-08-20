#!/usr/bin/env python3
"""Sync compact Claude skill cards from official Anthropic GitHub repositories.

Dependency-free and non-interactive so it can run unattended in GitHub Actions.

Layout produced (see Claude/README.md):
    Claude/skills/<YYYY-MM-DD>/skills/<slug>.md   one compact card per skill
    Claude/skills/<YYYY-MM-DD>/skills/catalog.json  index + shared defaults + CLI reference
    Claude/Changelogs/<YYYY-MM-DD>.txt              diff against the previous snapshot
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CLAUDE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
KST = timezone(timedelta(hours=9), "KST")

RAW = "https://raw.githubusercontent.com"
SKILLS_REPO = "anthropics/skills"
SKILLS_BRANCH = "main"
CODE_REPO = "anthropics/claude-code"
CODE_BRANCH = "main"

# Rule 4: only coding / programming / documentation skills are converted.
# Slug families win over description hints: several document skills describe what
# they are *not* good for ("general coding tasks"), which fools a bare keyword scan.
DOCUMENT_SLUGS = frozenset(
    {
        "docx", "pdf", "pptx", "xlsx", "doc-coauthoring", "internal-comms",
        "brand-guidelines", "theme-factory", "canvas-design",
    }
)
CODING_HINTS = (
    "mcp", "server", "api", "sdk", "code", "coding", "debug", "test", "testing",
    "frontend", "react", "css", "html", "javascript", "typescript", "python",
    "artifact", "webapp", "web app", "component", "skill", "plugin", "script",
)
DOCUMENT_HINTS = (
    "document", "presentation", "slide", "deck", "spreadsheet", "report", "memo",
    "writing", "draft", "guideline", "communication", "newsletter", "co-author",
)
EXCLUDE_SLUGS = frozenset({"academy-guide", "discernment-nudge"})

# Shared boilerplate is emitted once under catalog["defaults"] instead of being
# repeated in every card (rule 7).
DEFAULT_PROCEDURE = (
    "Confirm the skill trigger matches the request before loading it.",
    "Read only the sections of the skill needed for the current step.",
    "Prefer the skill's own scripts and helpers over ad hoc reimplementation.",
    "Verify with the narrowest relevant command.",
)
DEFAULT_TOKEN_POLICY = (
    "Load skill bodies on demand; keep only the trigger line resident.",
    "Link to the upstream path instead of copying long documents.",
    "Share catalog defaults instead of repeating them per card.",
)
DEFAULT_COMPATIBILITY = (
    "Do not overwrite existing dated skill snapshots.",
    "Integrate only if the slug is unique or the content hash changed.",
    "Preserve changelog evidence for every generated update.",
)

# Built-in Claude Code slash commands, migrated from the legacy
# Claude/skills/SKILLS_CATALOG.yaml so no prior reference is lost (rule 17).
# Newly announced commands are merged in from the CHANGELOG delta each run.
SEED_COMMANDS: dict[str, str] = {
    "/init": "Generate CLAUDE.md with codebase architecture, conventions, commands",
    "/review": "Multi-pass PR review; checks logic, style, security, tests",
    "/security-review": "OWASP-focused audit of pending diffs; risk-ranked findings",
    "/simplify": "Review changed code for reuse/quality/efficiency, then fix issues",
    "/session-start-hook": "Create SessionStart hook so web sessions can run tests and linters",
    "/update-config": "Configure settings.json; hooks, permissions, env vars",
    "/keybindings-help": "Customize ~/.claude/keybindings.json; supports chord bindings",
    "/fewer-permission-prompts": "Scan transcripts, add bash/MCP allowlist to .claude/settings.json",
    "/loop": "Run a prompt or slash command on a recurring interval (default 10m)",
    "/claude-api": "Build/debug Claude API apps; prompt caching, tool use, model migration",
    "/ultrareview": "Parallel multi-agent code review; no-arg=local branch, arg=GitHub PR",
    "/ultraplan": "Auto-create cloud worktrees/environments for multi-agent planning",
    "/team-onboarding": "Generate onboarding guide from local Claude Code usage history",
    "/effort": "Interactive slider for session effort level (env: CLAUDE_EFFORT)",
    "/powerup": "Interactive animated feature demos with lessons",
    "/tui": "Switch to flicker-free alt-screen TUI rendering (env: CLAUDE_CODE_NO_FLICKER)",
    "/focus": "Toggle focus view: prompt + tool summary + final response only",
    "/undo": "Alias for /rewind; undoes the last assistant action",
    "/usage": "Show token usage and cost stats (merged /cost + /stats)",
    "/theme": "Create or switch custom color themes",
    "/color": "Set session color (no args = random pick)",
}

# Hook lifecycle events, migrated from the legacy catalog.
SEED_HOOKS: dict[str, str] = {
    "PreToolUse": "Before any tool runs; can block (exit 2 or {decision:'block'})",
    "PostToolUse": "After a tool completes; log results, trigger follow-ups",
    "Notification": "On push-notification events; forward alerts",
    "Stop": "After an assistant turn completes; post-turn logging",
    "SubagentStop": "After a subagent turn completes; aggregate results",
    "PreCompact": "Before compaction; can block critical operations",
    "TaskCreated": "When a task is created via TaskCreate",
    "WorktreeCreate": "On worktree creation; HTTP type returns worktreePath",
    "PermissionDenied": "After auto-mode denial; return {retry:true} to re-run",
}
HOOK_INVOKE_TYPES = ("shell", "mcp_tool", "http")

# Changelog prose mentions plenty of backticked tokens that are not Claude Code
# configuration (shell variables, hostnames, error codes). Only accept tokens that
# look like Claude Code's own knobs.
ENV_PREFIXES = ("ANTHROPIC_", "CLAUDE_", "OTEL_", "MCP_", "AWS_", "DISABLE_", "ENABLE_")
SETTING_ROOTS = frozenset(
    {
        "sandbox", "permissions", "hooks", "env", "statusLine", "autoMode",
        "attribution", "worktree", "model", "outputStyle", "mcp", "plugins", "skills",
    }
)

SEED_SETTINGS: dict[str, str] = {
    "skillOverrides": "off | user-invocable-only | name-only",
    "autoScrollEnabled": "bool; auto-scroll in fullscreen TUI mode",
    "showThinkingSummaries": "bool; thinking summary generation",
    "disableSkillShellExecution": "bool; inline shell execution in skill definitions",
    "prUrlTemplate": "string; custom URL template for the PR footer badge",
    "sandbox.network.deniedDomains": "list[string]; block domains despite allowlists",
}

SEED_ENV: dict[str, str] = {
    "CLAUDE_EFFORT": "Current effort level; usable in skill template strings",
    "CLAUDE_CODE_NO_FLICKER": "1 = alt-screen flicker-free rendering (same as /tui)",
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1 = PowerShell tool (Windows opt-in preview)",
    "CLAUDE_STREAM_IDLE_TIMEOUT_MS": "Integer ms for the streaming idle watchdog",
    "OTEL_LOG_RAW_API_BODIES": "1 = emit full API bodies as OTEL events",
    "DISABLE_UPDATES": "1 = block all update paths including manual 'claude update'",
    "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY": "1 = gateway /v1/models discovery",
}


def request_text(url: str, attempts: int = 3) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "prompt-guide-claude-skill-sync"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError:
            raise
        except urllib.error.URLError:
            if attempt == attempts:
                raise
            time.sleep(2**attempt)
    raise urllib.error.URLError("unreachable")


def optional_text(url: str) -> str:
    try:
        return request_text(url)
    except urllib.error.URLError:
        return ""


def discover_slugs() -> list[str]:
    """Read the official plugin marketplace manifest to enumerate skills."""
    raw = request_text(f"{RAW}/{SKILLS_REPO}/{SKILLS_BRANCH}/.claude-plugin/marketplace.json")
    manifest = json.loads(raw)
    slugs: list[str] = []
    for plugin in manifest.get("plugins", []):
        for entry in plugin.get("skills", []):
            slug = str(entry).rstrip("/").split("/")[-1]
            if slug and slug not in slugs:
                slugs.append(slug)
    return sorted(slugs)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Minimal YAML frontmatter reader: scalars, quoted scalars, block scalars."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    body = text[text.find("\n") + 1 : end + 1]
    fields: dict[str, str] = {}
    key: str | None = None
    block: list[str] = []

    def flush() -> None:
        if key is not None:
            fields[key] = " ".join(part.strip() for part in block if part.strip())

    for line in body.splitlines():
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if match and not line.startswith((" ", "\t")):
            flush()
            key, value = match.group(1), match.group(2).strip()
            if value in {"|", "|-", "|+", ">", ">-", ">+"}:
                block = []
            else:
                block = [value.strip("'\"")]
        elif key is not None:
            block.append(line)
    flush()
    return fields


def split_trigger(text: str, limit: int = 200) -> tuple[str, str]:
    """Return (first sentence, remainder) so no card repeats its own trigger."""
    text = re.sub(r"\s+", " ", text).strip()
    match = re.search(r"(?<=[.!?])\s", text)
    if match:
        return compact_text(text[: match.start()], limit), text[match.end() :]
    return compact_text(text, limit), ""


def compact_text(text: str, max_chars: int = 240) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    clipped = text[: max_chars - 1]
    cut = clipped.rfind(" ")
    if cut > max_chars // 2:
        clipped = clipped[:cut]
    return clipped.rstrip(" ,;:(-") + "…"


def classify(slug: str, description: str) -> str:
    if slug in DOCUMENT_SLUGS:
        return "documentation"
    blob = f"{slug} {description}".lower()
    if any(hint in blob for hint in CODING_HINTS):
        return "coding"
    if any(hint in blob for hint in DOCUMENT_HINTS):
        return "documentation"
    return "other"


def card_hash(card: dict[str, Any]) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill(slug: str, text: str) -> dict[str, Any] | None:
    fields = parse_frontmatter(text)
    description = fields.get("description", "")
    if not description:
        return None
    category = classify(slug, description)
    if category == "other" or slug in EXCLUDE_SLUGS:
        return None
    trigger, remainder = split_trigger(description)
    card = {
        "slug": slug,
        "name": fields.get("name", slug),
        "category": category,
        "source": f"https://github.com/{SKILLS_REPO}/tree/{SKILLS_BRANCH}/skills/{slug}",
        "source_path": f"skills/{slug}/SKILL.md",
        "trigger": trigger,
        "detail": compact_text(remainder),
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
        "",
        "## Trigger",
        "",
        card["trigger"],
        "",
    ]
    if card["detail"]:
        lines += ["## Detail", "", card["detail"], ""]
    lines += [
        "## Defaults",
        "",
        "Procedure, token policy, and compatibility rules are shared; see"
        " `catalog.json` -> `defaults`.",
        "",
    ]
    return "\n".join(lines)


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def parse_changelog(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    matches = list(re.finditer(r"^##\s+\[?(\d+\.\d+\.\d+)\]?", text, flags=re.MULTILINE))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match.group(1), text[match.end() : end].strip()))
    return sections


def changelog_delta(sections: list[tuple[str, str]], previous: str) -> list[tuple[str, str]]:
    if not previous:
        return sections[:1]
    try:
        floor = version_key(previous)
    except ValueError:
        return sections[:1]
    return [item for item in sections if version_key(item[0]) > floor]


def describe_from_delta(delta: list[tuple[str, str]], token: str) -> str:
    """Pull the shortest changelog bullet that introduces `token`."""
    best = ""
    for _, body in delta:
        for line in body.splitlines():
            line = line.strip().lstrip("-").strip()
            if f"`{token}`" not in line and token not in line:
                continue
            cleaned = compact_text(line, 160)
            if cleaned and (not best or len(cleaned) < len(best)):
                best = cleaned
    return best


def merge_cli_reference(previous: dict[str, Any], delta: list[tuple[str, str]]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    """Carry the CLI reference forward and merge items announced in the delta."""
    base = previous.get("claude_code", {}) if previous else {}
    commands = dict(SEED_COMMANDS) | dict(base.get("commands", {}))
    hooks = dict(SEED_HOOKS) | dict(base.get("hooks", {}))
    settings = dict(SEED_SETTINGS) | dict(base.get("settings", {}))
    env = dict(SEED_ENV) | dict(base.get("env", {}))

    found: dict[str, list[str]] = {"commands": [], "settings": [], "env": []}
    joined = "\n".join(body for _, body in delta)

    for token in sorted(set(re.findall(r"`(/[a-z][a-z0-9-]{2,})`", joined))):
        if token not in commands:
            commands[token] = describe_from_delta(delta, token) or "Announced in the Claude Code changelog."
            found["commands"].append(token)
    for token in sorted(set(re.findall(r"`([A-Z][A-Z0-9_]{5,})`", joined))):
        if token not in env and token.startswith(ENV_PREFIXES):
            env[token] = describe_from_delta(delta, token) or "Announced in the Claude Code changelog."
            found["env"].append(token)
    for token in sorted(set(re.findall(r"`([a-z][a-zA-Z0-9]*(?:\.[a-zA-Z][a-zA-Z0-9]*)+)`", joined))):
        segments = token.split(".")
        looks_like_setting = segments[0] in SETTING_ROOTS or any(
            segment != segment.lower() for segment in segments
        )
        if token not in settings and looks_like_setting:
            settings[token] = describe_from_delta(delta, token) or "Announced in the Claude Code changelog."
            found["settings"].append(token)

    reference = {
        "commands": dict(sorted(commands.items())),
        "hooks": dict(sorted(hooks.items())),
        "hook_invoke_types": list(HOOK_INVOKE_TYPES),
        "settings": dict(sorted(settings.items())),
        "env": dict(sorted(env.items())),
    }
    return reference, found


def current_date() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d")


def previous_catalog(today: str) -> dict[str, Any]:
    if not SKILLS_ROOT.exists():
        return {}
    candidates = [
        path / "skills" / "catalog.json"
        for path in SKILLS_ROOT.iterdir()
        if path.is_dir() and path.name < today and (path / "skills" / "catalog.json").exists()
    ]
    if candidates:
        return json.loads(sorted(candidates)[-1].read_text(encoding="utf-8"))
    # Bootstrap: a checkout still on the pre-snapshot layout only has a flat pin.
    legacy_pin = SKILLS_ROOT / ".version"
    if legacy_pin.exists():
        return {"claude_code_version": legacy_pin.read_text(encoding="utf-8").strip()}
    return {}


def ensure_unique(cards: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for card in cards:
        slug = card["slug"]
        if slug in seen:
            duplicates.add(slug)
        seen.add(slug)
    if duplicates:
        raise ValueError(f"Duplicate skill slugs: {', '.join(sorted(duplicates))}")


def compare(previous: dict[str, Any], cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    prev_by_slug = {item["slug"]: item for item in previous.get("skills", []) if "slug" in item}
    next_by_slug = {card["slug"]: card for card in cards}
    modified = sorted(
        slug
        for slug in set(prev_by_slug) & set(next_by_slug)
        if prev_by_slug[slug].get("hash") != next_by_slug[slug].get("hash")
    )
    return {
        "added": sorted(set(next_by_slug) - set(prev_by_slug)),
        "modified": modified,
        "deleted": sorted(set(prev_by_slug) - set(next_by_slug)),
        "unchanged": sorted((set(prev_by_slug) & set(next_by_slug)) - set(modified)),
    }


def write_snapshot(today: str, cards: list[dict[str, Any]], version: str, reference: dict[str, Any]) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")

    catalog = {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official Anthropic GitHub repositories only",
        "sources": {
            "skills": f"https://github.com/{SKILLS_REPO}",
            "claude_code": f"https://github.com/{CODE_REPO}",
        },
        "claude_code_version": version,
        "defaults": {
            "procedure": list(DEFAULT_PROCEDURE),
            "token_policy": list(DEFAULT_TOKEN_POLICY),
            "compatibility": list(DEFAULT_COMPATIBILITY),
        },
        "claude_code": reference,
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return skills_dir


def write_changelog(
    today: str,
    diff: dict[str, list[str]],
    found: dict[str, list[str]],
    previous_version: str,
    version: str,
    skills_dir: Path,
    conflicts: list[str],
) -> Path:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {value}" for value in values] if values else ["- none"]

    def cli_lines(items: dict[str, list[str]], cap: int = 12) -> list[str]:
        rendered = []
        for kind in ("commands", "settings", "env"):
            values = items[kind]
            if not values:
                continue
            shown = ", ".join(values[:cap])
            extra = f" 외 {len(values) - cap}개" if len(values) > cap else ""
            rendered.append(f"- {kind}(+{len(values)}): {shown}{extra}")
        return rendered or ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: {skills_dir.relative_to(CLAUDE_ROOT.parent)}",
        f"Claude Code: {previous_version or 'none'} -> {version}",
        "Source: official Anthropic GitHub repositories",
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
        "[신규 CLI 항목]",
        *cli_lines(found),
        "",
        "[최적화된 구조]",
        f"- 날짜별 스냅샷 구조 유지: skills/{today}/skills",
        "- 각 스킬 카드는 slug, category, source, trigger, detail만 보관",
        "- 공통 procedure/token_policy/compatibility는 catalog.json defaults로 1회만 기록",
        "- 슬래시 커맨드/훅/설정/환경변수는 catalog.json claude_code로 통합",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 카드마다 반복되던 보일러플레이트 3블록을 defaults 참조로 대체",
        "- 상위 문서 원문 복사 대신 upstream 경로 링크만 저장",
        "- description은 trigger 1문장 + summary 240자로 상한 적용",
        "- 코딩/문서 작업 외 스킬은 스냅샷에서 제외",
        "",
        "[충돌 해결 내역]",
        *bullets(conflicts),
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
    today = current_date()
    previous = previous_catalog(today)

    cards: list[dict[str, Any]] = []
    skipped: list[str] = []
    for slug in discover_slugs():
        text = optional_text(f"{RAW}/{SKILLS_REPO}/{SKILLS_BRANCH}/skills/{slug}/SKILL.md")
        if not text:
            skipped.append(f"{slug}: SKILL.md unreachable, previous snapshot retained")
            continue
        card = build_skill(slug, text)
        if card is None:
            continue
        cards.append(card)

    if not cards:
        print("No skills resolved from the official marketplace manifest.", file=sys.stderr)
        return 1
    ensure_unique(cards)
    cards.sort(key=lambda card: (card["category"], card["slug"]))

    sections = parse_changelog(request_text(f"{RAW}/{CODE_REPO}/{CODE_BRANCH}/CHANGELOG.md"))
    if not sections:
        print("Could not parse the Claude Code changelog.", file=sys.stderr)
        return 1
    version = sections[0][0]
    previous_version = str(previous.get("claude_code_version", ""))
    reference, found = merge_cli_reference(previous, changelog_delta(sections, previous_version))

    diff = compare(previous, cards)
    conflicts = [
        "slug 기준으로 중복 스킬 통합",
        "기존 날짜 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "변경 감지는 hash 비교로 수행",
        "CLI 레퍼런스는 이전 스냅샷을 이어받아 신규 항목만 병합",
        *skipped,
    ]

    skills_dir = write_snapshot(today, cards, version, reference)
    changelog = write_changelog(today, diff, found, previous_version, version, skills_dir, conflicts)

    print(f"Synced {len(cards)} Claude skills to {skills_dir.relative_to(CLAUDE_ROOT.parent)}")
    print(f"Claude Code version: {previous_version or 'none'} -> {version}")
    print(f"Changelog: {changelog.relative_to(CLAUDE_ROOT.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

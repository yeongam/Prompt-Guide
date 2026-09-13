#!/usr/bin/env python3
"""Daily Claude Code skills updater.

Fetches the official changelog from anthropics/claude-code, refreshes the
canonical Claude/skills/SKILLS_CATALOG.yaml, and writes a dated skill-card
snapshot plus changelog under Claude/, mirroring the GPT/ sync routine.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).parent.parent
CLAUDE_ROOT = REPO_ROOT / "Claude"
CATALOG_FILE = CLAUDE_ROOT / "skills" / "SKILLS_CATALOG.yaml"
VERSION_FILE = CLAUDE_ROOT / "skills" / ".version"
SKILLS_ROOT = CLAUDE_ROOT / "skills"
CHANGELOGS_ROOT = CLAUDE_ROOT / "Changelogs"
CHANGELOG_SRC = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"

# Coding/programming/documentation-focused skills carried in SKILLS_CATALOG.yaml.
# These are converted into standalone dated skill cards on every sync.
CODING_SKILLS: tuple[str, ...] = (
    "init",
    "review",
    "security-review",
    "simplify",
    "session-start-hook",
    "update-config",
    "claude-api",
    "fewer-permission-prompts",
    "keybindings-help",
)


@dataclass(frozen=True)
class SkillDef:
    slug: str
    cmd: str
    trigger: str
    desc: str


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-skills-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def split_versions(changelog: str) -> list[tuple[str, str]]:
    """Return [(version, section_text), ...] newest first."""
    matches = list(re.finditer(r"^##\s+\[?(\d+\.\d+\.\d+)\]?", changelog, flags=re.MULTILINE))
    sections = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(changelog)
        sections.append((m.group(1), changelog[start:end].strip()))
    return sections


def current_version() -> str:
    return VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else ""


def extract_new_items(section: str) -> dict:
    skills = list(set(re.findall(r"`(/[\w-]+)`", section)))
    settings = list(set(re.findall(r"`([a-zA-Z][a-zA-Z.]+)`(?=\s*[–—-])", section)))
    env_vars = list(set(re.findall(r"`([A-Z][A-Z_]{3,})`", section)))
    hooks = list(set(re.findall(r"\b(Pre\w+|Post\w+|TaskCreated|WorktreeCreate|PermissionDenied|Notification|Stop|SubagentStop)\b", section)))
    return {"skills": skills, "settings": settings, "env": env_vars, "hooks": hooks}


def update_catalog_version_field(ver: str) -> None:
    if not CATALOG_FILE.exists():
        return
    text = CATALOG_FILE.read_text()
    text = re.sub(r"^version:.*$", f"version: {ver}", text, flags=re.MULTILINE)
    text = re.sub(r"^updated:.*$", f"updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}", text, flags=re.MULTILINE)
    CATALOG_FILE.write_text(text)


def parse_catalog_skills() -> dict[str, SkillDef]:
    """Pull cmd/trigger/desc for CODING_SKILLS out of the YAML catalog without a YAML dependency."""
    if not CATALOG_FILE.exists():
        return {}
    text = CATALOG_FILE.read_text()
    out: dict[str, SkillDef] = {}
    for slug in CODING_SKILLS:
        m = re.search(rf"^  {re.escape(slug)}:\n((?:    .+\n?)+)", text, flags=re.MULTILINE)
        if not m:
            continue
        block = m.group(1)

        def field(name: str) -> str:
            fm = re.search(rf"^    {name}:\s*(.+)$", block, flags=re.MULTILINE)
            return fm.group(1).strip() if fm else ""

        out[slug] = SkillDef(slug=slug, cmd=field("cmd"), trigger=field("trigger"), desc=field("desc"))
    return out


def card_hash(card: dict) -> str:
    encoded = json.dumps(card, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_skill_card(skill: SkillDef, ver: str) -> dict:
    card = {
        "name": skill.slug,
        "slug": skill.slug,
        "cmd": skill.cmd,
        "source": "https://github.com/anthropics/claude-code",
        "source_version": ver,
        "trigger": skill.trigger,
        "output": skill.desc,
        "token_policy": [
            "One canonical line per skill; no restated background context.",
            "Reference SKILLS_CATALOG.yaml instead of duplicating full docs.",
        ],
        "compatibility": [
            "Do not overwrite existing dated skill snapshots.",
            "Integrate only if slug is unique or content hash changed.",
            "Preserve changelog evidence for every generated update.",
        ],
    }
    card["hash"] = card_hash(card)
    return card


def skill_markdown(card: dict) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"- Command: `{card['cmd']}`" if card["cmd"] else "- Command: (none)",
        f"- Source: {card['source']}",
        f"- Source version: `{card['source_version']}`",
        f"- Trigger: {card['trigger']}",
        "",
        "## Output",
        "",
        str(card["output"]),
        "",
        "## Token Policy",
        "",
        *[f"- {i}" for i in card["token_policy"]],
        "",
        "## Compatibility",
        "",
        *[f"- {i}" for i in card["compatibility"]],
        "",
    ]
    return "\n".join(lines)


def previous_catalog(today: str) -> dict:
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


def write_skill_snapshot(today: str, cards: list[dict], ver: str) -> Path:
    skills_dir = SKILLS_ROOT / today / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (skills_dir / f"{card['slug']}.md").write_text(skill_markdown(card), encoding="utf-8")
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "date": today,
        "directory_rule": "YYYY-MM-DD/skills",
        "source_policy": "official anthropics/claude-code GitHub repository only",
        "source_version": ver,
        "skills": cards,
    }
    (skills_dir / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return skills_dir


def compare(prev: dict, cards: list[dict]) -> dict[str, list[str]]:
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


def write_changelog(today: str, prev_ver: str, ver: str, diff: dict, skills_dir: Path, raw_section: str) -> Path:
    CHANGELOGS_ROOT.mkdir(parents=True, exist_ok=True)

    def bullets(values: list[str]) -> list[str]:
        return [f"- {slug}" for slug in values] if values else ["- none"]

    lines = [
        f"Prompt-Guide Claude Skills Changelog - {today}",
        "",
        f"Snapshot: Claude/skills/{today}/skills",
        f"Catalog : Claude/skills/SKILLS_CATALOG.yaml",
        "Source  : official anthropics/claude-code GitHub repository",
        f"Version : {prev_ver or 'none'} -> {ver}",
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
        "- 각 스킬은 trigger, output, token_policy, compatibility로 경량화",
        "- 카탈로그 원본(SKILLS_CATALOG.yaml)은 단일 소스로 유지, 스냅샷은 참조만 저장",
        "",
        "[토큰 절감 관련 변경 사항]",
        "- 공식 체인지로그 원문 전체 복사 대신 최신 버전 구간만 발췌",
        "- 스킬 카드마다 해시 기반 변경 감지로 불필요한 재작성 방지",
        "- 반복 설명 대신 SKILLS_CATALOG.yaml 참조로 통합",
        "",
        "[충돌 해결 내역]",
        "- slug 기준으로 중복 스킬 통합",
        "- 기존 날짜 스킬 스냅샷은 덮어쓰지 않고 신규 날짜에 기록",
        "- 변경 감지는 hash 비교로 수행",
        "",
        "[요약]",
        (
            f"- skills: added={len(diff['added'])}, modified={len(diff['modified'])}, "
            f"deleted={len(diff['deleted'])}, unchanged={len(diff['unchanged'])}"
        ),
        "",
        "-" * 40,
        "[공식 체인지로그 발췌 / Official changelog excerpt (latest version)]",
        "",
        raw_section[:3000],
        "",
    ]
    path = CHANGELOGS_ROOT / f"{today}.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    print("Fetching Claude Code changelog...")
    try:
        changelog = fetch(CHANGELOG_SRC)
    except urllib.error.URLError as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 1

    sections = split_versions(changelog)
    if not sections:
        print("Could not parse any version.", file=sys.stderr)
        return 1

    ver, latest_section = sections[0]
    prev = current_version()
    print(f"Latest: {ver}  |  Local: {prev or 'none'}")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    catalog_skills = parse_catalog_skills()
    cards = [build_skill_card(catalog_skills[slug], ver) for slug in CODING_SKILLS if slug in catalog_skills]

    prev_catalog = previous_catalog(today)
    skills_dir = write_skill_snapshot(today, cards, ver)
    diff = compare(prev_catalog, cards)
    changelog_path = write_changelog(today, prev, ver, diff, skills_dir, latest_section)

    if ver != prev:
        VERSION_FILE.write_text(ver)
        update_catalog_version_field(ver)
        print(f"Updated: {prev or 'none'} -> {ver}")
    else:
        print("Catalog version already up to date; refreshed dated snapshot only.")

    print(f"Snapshot : {skills_dir.relative_to(REPO_ROOT)}")
    print(f"Changelog: {changelog_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

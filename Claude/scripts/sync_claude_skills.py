#!/usr/bin/env python3
"""Sync compact Claude Code skill cards from official Anthropic repos.

Source of truth: anthropics/claude-code (CHANGELOG.md + .claude-plugin/marketplace.json).
Plugin bodies are read from the repo each marketplace entry points to
(anthropics/claude-plugins-official).

Output (never overwrites older dates):
  Claude/skills/YYYY-MM-DD/skills/{core.yaml,_shared.md,catalog.json,<slug>/SKILL.md}
  Claude/Changelogs/YYYY-MM-DD.txt
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # Claude/
SKILLS = ROOT / "skills"
LOGS = ROOT / "Changelogs"
CC_URL = "https://github.com/anthropics/claude-code.git"
KST = timezone(timedelta(hours=9))
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Only coding / programming / documentation related categories are converted.
KEEP_CATEGORIES = {"development", "productivity", "security"}
MAX_DESC, MAX_STEPS, MAX_STEP, INLINE = 200, 5, 80, 900


def sh(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True).stdout.strip()


def clone(url: str, dest: Path) -> str:
    if not dest.exists():
        sh("git", "clone", "--depth", "1", "-q", url, str(dest))
    return sh("git", "rev-parse", "HEAD", cwd=dest)


def frontmatter(text: str) -> tuple[dict, str]:
    meta: dict = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                m = re.match(r"^([\w-]+):\s*(.*)$", line)
                if m:
                    meta[m.group(1)] = m.group(2).strip().strip("\"'")
            text = text[end + 4:]
    return meta, text


def clip(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def steps(body: str) -> list[str]:
    """Headings + numbered items, dynamic `!` context and code stripped."""
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    out: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^\s*(?:#{2,3}\s+|\d+[.)]\s+)(.+)$", line)
        if not m or "!`" in line:
            continue
        item = clip(re.sub(r"[*_`]", "", m.group(1)), MAX_STEP)
        if item and item.lower() not in {s.lower() for s in out}:
            out.append(item)
        if len(out) == MAX_STEPS:
            break
    return out


def card(c: dict) -> str:
    lines = [
        "---",
        f"name: {c['slug']}",
        f"description: {json.dumps(c['description'], ensure_ascii=False)}",
        *([f"allowed-tools: {c['tools']}"] if c["inline"] and c["kind"] == "command" and c["tools"] else []),
        "---",
        f"`{c['kind']}` · plugin `{c['plugin']}`" + (f" · `{c['invoke']}`" if c["invoke"] else ""),
        f"Src: {c['source']}",
    ]
    if c["tools"] and not (c["inline"] and c["kind"] == "command"):
        lines.append(f"Tools: {c['tools']}")
    if c["inline"]:
        lines += ["", c["inline"]]
    elif c["steps"]:
        lines += ["Outline (full text at Src):", *[f"{i}. {s}" for i, s in enumerate(c["steps"], 1)]]
    return "\n".join(lines) + "\n"


def collect(cc: Path, tmp: Path, core_names: set[str]) -> tuple[list[dict], list[str]]:
    market = json.loads((cc / ".claude-plugin" / "marketplace.json").read_text())
    repos: dict[str, tuple[Path, str]] = {}
    raw: list[dict] = []
    for p in market.get("plugins", []):
        if p.get("category") not in KEEP_CATEGORIES:
            continue
        src = p.get("source")
        if isinstance(src, str):
            base, url, sha = cc / src, "https://github.com/anthropics/claude-code", sh("git", "rev-parse", "HEAD", cwd=cc)
        else:
            url = src["url"].removesuffix(".git")
            if url not in repos:
                d = tmp / re.sub(r"\W", "_", url)
                repos[url] = (d, clone(src["url"], d))
            d, sha = repos[url]
            base = d / src.get("path", "")
        files = [(f, "command") for f in sorted(base.glob("commands/*.md"))]
        files += [(f, "agent") for f in sorted(base.glob("agents/*.md"))]
        files += [(f, "skill") for f in sorted(base.glob("skills/*/SKILL.md"))]
        for f, kind in files:
            name = f.parent.name if kind == "skill" else f.stem
            if kind == "command" and name == "help":
                continue  # per-plugin help duplicates README/desc
            text = f.read_text(encoding="utf-8")
            meta, body = frontmatter(text)
            rel = f.relative_to(base.parent.parent if src and not isinstance(src, str) else cc)
            raw.append({
                "plugin": p["name"], "name": meta.get("name", name).replace("_", "-"), "kind": kind,
                "description": clip(meta.get("description") or p.get("description", ""), MAX_DESC),
                "invoke": f"/{p['name']}:{name}" if kind == "command" else "",
                "tools": clip(meta.get("allowed-tools") or meta.get("tools", ""), 120),
                "source": f"{url}/blob/{sha[:12]}/{rel.as_posix()}",
                "steps": steps(body),
                "inline": re.sub(r"\n{3,}", "\n\n", body.strip()) if len(body.strip()) <= INLINE else "",
                "hash": hashlib.sha256(text.encode()).hexdigest()[:16],
            })
    # Naming: <plugin>-<name> (bare <plugin> when name == plugin); core built-ins win on clash.
    conflicts: list[str] = []
    for c in raw:
        n, pl = c["name"], c["plugin"]
        c["slug"] = n if n == pl or n.startswith(pl + "-") else f"{pl}-{n}"
        if c["slug"] in core_names:
            conflicts.append(f"{c['slug']} ({pl}) -> {c['slug']}-plugin [core built-in /{c['slug']} 우선]")
            c["slug"] += "-plugin"
    return raw, conflicts


def yaml_keys(path: Path, sections=("commands", "skills", "hooks")) -> dict[str, str]:
    """Flat {section.key: block-hash} from a simple 2-space YAML file."""
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    sec = key = None
    buf: list[str] = []

    def flush():
        if sec and key:
            out[f"{'commands' if sec == 'skills' else sec}.{key}"] = hashlib.sha1("".join(buf).encode()).hexdigest()[:8]

    for line in path.read_text().splitlines(True):
        if re.match(r"^\S", line):
            flush(); key = None; buf = []
            m = re.match(r"^(\w+):", line)
            sec = m.group(1) if m and m.group(1) in sections else None
        elif sec and (m := re.match(r"^  ([\w.-]+):", line)):
            flush(); key, buf = m.group(1), [line]
        elif key:
            buf.append(line)
    flush()
    out.pop("hooks.hook_invoke_types", None)
    return out


def previous_snapshot(date: str) -> Path | None:
    olds = sorted(p for p in SKILLS.iterdir() if p.is_dir() and DATE_RE.match(p.name) and p.name < date)
    return olds[-1] / "skills" if olds else None


def bullet(items) -> list[str]:
    items = list(items)
    return [f"- {i}" for i in items] or ["- none"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.now(KST).strftime("%Y-%m-%d"))
    ap.add_argument("--cc", type=Path, help="existing anthropics/claude-code checkout")
    args = ap.parse_args()

    out = SKILLS / args.date / "skills"
    prev = previous_snapshot(args.date)
    legacy = SKILLS / "SKILLS_CATALOG.yaml"
    prev_core = prev / "core.yaml" if prev else legacy

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        cc = args.cc or tmp / "cc"
        cc_sha = clone(CC_URL, cc)
        changelog = (cc / "CHANGELOG.md").read_text()
        latest = re.search(r"^## \[?(\d+\.\d+\.\d+)", changelog, re.M).group(1)
        m = re.search(r"^version:\s*(\S+)", prev_core.read_text(), re.M) if prev_core.exists() else None
        cut = changelog.find(f"## {m.group(1)}\n") if m else -1
        delta = changelog[: cut if cut > 0 else len(changelog)]

        out.mkdir(parents=True, exist_ok=True)
        core = out / "core.yaml"
        if not core.exists():  # carry forward last curated core, bump version
            for f in ("core.yaml", "_shared.md"):
                if prev and (prev / f).exists():
                    shutil.copy2(prev / f, out / f)
        if core.exists():
            txt = re.sub(r"^version:.*$", f"version: {latest}", core.read_text(), flags=re.M)
            core.write_text(re.sub(r"^updated:.*$", f"updated: {args.date}", txt, flags=re.M))
        core_now = yaml_keys(core)
        core_names = {k.split(".", 1)[1] for k in core_now if k.startswith("commands.")}

        cards, conflicts = collect(cc, tmp, core_names)
        pending = sorted({x for x in re.findall(r"^- Added `?/([a-z][\w-]*)", delta, re.M)} - core_names)

    for d in out.iterdir():  # regenerate this date's cards only
        if d.is_dir():
            shutil.rmtree(d)
    for c in cards:
        (out / c["slug"]).mkdir()
        (out / c["slug"] / "SKILL.md").write_text(card(c), encoding="utf-8")
    catalog = {
        "date": args.date, "directory_rule": "YYYY-MM-DD/skills", "core_version": latest,
        "source": {"claude-code": cc_sha[:12]},
        "skills": {c["slug"]: {k: c[k] for k in ("plugin", "kind", "invoke", "hash")} for c in cards},
    }
    rows = ",\n".join(f" {json.dumps(k)}: {json.dumps(v, sort_keys=True)}" for k, v in sorted(catalog.pop("skills").items()))
    head = json.dumps(catalog, ensure_ascii=False, sort_keys=True)[:-1]
    (out / "catalog.json").write_text(f"{head}, \"skills\": {{\n{rows}\n}}}}\n")

    # Diff vs previous snapshot.
    old_cards = {}
    if prev and (prev / "catalog.json").exists():
        old_cards = {k: v["hash"] for k, v in json.loads((prev / "catalog.json").read_text())["skills"].items()}
    new_cards = {c["slug"]: c["hash"] for c in cards}
    core_old = yaml_keys(prev_core)
    add = sorted(f"[plugin] {k}" for k in new_cards.keys() - old_cards.keys())
    add += sorted(f"[core] {k}" for k in core_now.keys() - core_old.keys())
    mod = sorted(f"[plugin] {k}" for k in new_cards.keys() & old_cards.keys() if new_cards[k] != old_cards[k])
    if prev_core == legacy:  # format migration: hashes not comparable
        same = core_now.keys() & core_old.keys()
        notes = [f"[core] {len(same)}개 기존 항목 compact 1줄 포맷으로 이전 (의미 변경은 아래 별도 표기)"]
    else:
        notes = []
        mod += sorted(f"[core] {k}" for k in core_now.keys() & core_old.keys() if core_now[k] != core_old[k])
    rm = sorted(f"[plugin] {k}" for k in old_cards.keys() - new_cards.keys())
    rm += sorted(f"[core] {k}" for k in core_old.keys() - core_now.keys())

    old_tok = sum(len(p.read_text()) for p in prev.rglob("*") if p.is_file()) // 4 if prev else (legacy.stat().st_size // 4 if legacy.exists() else 0)
    new_tok = sum(len(p.read_text()) for p in out.rglob("*") if p.is_file()) // 4
    LOGS.mkdir(exist_ok=True)
    log = [
        f"Claude Code Skills Changelog - {args.date}",
        f"Snapshot: Claude/skills/{args.date}/skills | Prev: {prev.parent.name if prev else 'legacy SKILLS_CATALOG.yaml'}",
        f"Source: anthropics/claude-code@{cc_sha[:12]} (v{latest})",
        "", "[추가된 스킬]", *bullet(add),
        "", "[수정된 스킬]", *bullet(mod + notes),
        "", "[삭제된 스킬]", *bullet(rm),
        "", "[최적화된 구조]",
        f"- 날짜별 스냅샷 유지: skills/{args.date}/skills (이전 날짜 덮어쓰지 않음)",
        "- core.yaml(내장 명령/훅/설정) + <slug>/SKILL.md(플러그인 카드) + catalog.json(해시)",
        "- 공통 규칙은 _shared.md 1곳으로 통합",
        "", "[토큰 절감 관련 변경 사항]",
        f"- core 카탈로그 추정 토큰: {len(prev_core.read_text()) // 4 if prev_core.exists() else 0} -> {len(core.read_text()) // 4 if core.exists() else 0} (chars/4)",
        f"- 스냅샷 전체 추정 토큰: {old_tok} -> {new_tok} (신규 카드 {len(cards)}개 포함)",
        f"- 카드당 설명 {MAX_DESC}자, 개요 {MAX_STEPS}단계 x {MAX_STEP}자 상한; 원문 {INLINE}자 이하만 인라인, 나머지는 링크",
        "", "[충돌 해결 내역]", *bullet(conflicts),
        "", "[core.yaml 미반영 신규 명령 (CHANGELOG 감지, 검토 필요)]", *bullet(f"/{x}" for x in pending),
        "", f"[요약] added={len(add)} modified={len(mod)} deleted={len(rm)} cards={len(cards)}",
    ]
    (LOGS / f"{args.date}.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    sys.exit(main())

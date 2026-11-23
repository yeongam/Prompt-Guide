# Claude Code Skills Routine

Entry: `python Claude/scripts/sync_claude_skills.py [--date YYYY-MM-DD]` (daily 00:00 KST via `.github/workflows/daily-skill-update.yml`).

- Source: `anthropics/claude-code` (CHANGELOG + plugin marketplace → `claude-plugins-official`).
- Snapshot: `Claude/skills/YYYY-MM-DD/skills/` — `core.yaml` (built-ins), `<plugin>-<name>/SKILL.md` (cards), `catalog.json` (hashes), `_shared.md` (common rules). Older dates are never overwritten.
- Changelog: `Claude/Changelogs/YYYY-MM-DD.txt`.
- `core.yaml` is carried forward and version-bumped automatically; new built-in commands in the CHANGELOG are curated into it by the routine.

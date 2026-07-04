# Claude Skill Sync Routine

This directory holds the daily Claude Code skill catalog, sourced only from
the official `anthropics/claude-code` repository's `CHANGELOG.md`.

The routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It refreshes the coding/programming/documentation skill catalog into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

Each dated snapshot contains one compact `.md` card per skill plus a
`catalog.json` (skills, settings, env, models — no upstream prose copied).
Existing dated snapshots are never overwritten; a new date gets a new
directory. Change detection between snapshots is by content hash.

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

listing added/modified/deleted skills, the structural/token optimizations
applied, and any naming conflicts resolved.

The dedicated GitHub Actions workflow (`.github/workflows/daily-skill-update.yml`)
runs this routine daily at 00:00 UTC and blocks routine changes outside `Claude/`.

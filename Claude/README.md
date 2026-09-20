# Claude Skill Sync Routine

This directory contains Claude Code-focused skill artifacts.

The routine entrypoint is:

```bash
python Claude/scripts/sync_claude_code_skills.py
```

It syncs compact skill cards from the official `anthropics/claude-code` GitHub repository into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

The dedicated GitHub Actions workflow runs this routine daily at 00:00 UTC and blocks routine changes outside `Claude/`.

`Claude/skills/SKILLS_CATALOG.yaml` stays as the compact single-file catalog (skills, hooks, settings, env vars, models) for quick low-token reference; the dated snapshots hold expanded per-skill cards with source commit provenance for auditing.

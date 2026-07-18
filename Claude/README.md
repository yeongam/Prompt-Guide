# Claude Skill Routine

This directory tracks Claude Code skill artifacts.

The routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It reads the official `anthropics/claude-code` changelog and syncs a compact,
dated skill snapshot into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

`Claude/skills/SKILLS_CATALOG.yaml` remains the master reference (version,
hooks, settings, env vars, models); dated snapshots under `skills/` are for
history and hash-based diffing only — they are never overwritten.

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

covering added/modified/deleted skills plus any newly relevant hooks,
settings, and env vars found upstream, structure/token-optimization notes,
and conflict-resolution notes.

The `.github/workflows/daily-skill-update.yml` workflow runs a related script
(`scripts/update_skills.py`) daily. Applying these artifacts to a live local
Claude Code runtime still requires an explicit local sync or install step.

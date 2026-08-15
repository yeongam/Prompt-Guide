# Claude Skill Routine

This directory contains Claude/Anthropic-focused skill artifacts.

The routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It syncs compact skill cards from official Anthropic GitHub repositories into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

The dedicated GitHub Actions workflow runs this routine daily at 00:00 KST and blocks
routine changes outside `Claude/`.

`Claude/skills/SKILLS_CATALOG.yaml` is an older, hand-maintained quick-reference catalog
of Claude Code CLI features (slash commands, hooks, settings). It is kept for reference
but is no longer the canonical source — the dated `Claude/skills/YYYY-MM-DD/skills/`
snapshots are.

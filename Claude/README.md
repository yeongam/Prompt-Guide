# Claude Skill Routine

This directory contains Claude Code-focused skill artifacts only.

The routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It syncs compact skill cards, sourced from the official `anthropics/claude-code`
repository (CHANGELOG.md version + best-effort commit), into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

listing added/modified/deleted skills, structure optimizations, token-saving
changes, and conflict resolutions for that run.

The flat `Claude/skills/SKILLS_CATALOG.yaml` and `Claude/skills/.version`
files are kept in sync for backward compatibility with existing readers.

This mirrors the `GPT/` directory's sync routine (see `GPT/README.md`) so both
assistants follow the same dated-snapshot, diff, and changelog conventions.

# Claude Code Skill Routine

This directory contains Claude Code-focused skill artifacts only.

The routine entrypoint is:

```bash
python scripts/update_skills.py
```

It syncs the canonical catalog and compact coding/programming/documentation
skill cards from the official `anthropics/claude-code` changelog into:

```text
Claude/skills/SKILLS_CATALOG.yaml   # single canonical catalog (version, triggers, desc)
Claude/skills/YYYY-MM-DD/skills/    # dated snapshot of skill cards + catalog.json
```

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

The dedicated GitHub Actions workflow (`.github/workflows/daily-skill-update.yml`)
runs this routine daily at 00:00 UTC against `main` and restricts routine changes
to `Claude/`.

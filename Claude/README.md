# Claude Skill and Hook Routine

This directory contains Claude Code-focused skill and hook artifacts only.

The routine entrypoints are:

```bash
python scripts/update_skills.py           # flat catalog: Claude/skills/SKILLS_CATALOG.yaml, .version
python Claude/scripts/sync_claude_skills.py  # dated snapshots: Claude/skills/YYYY-MM-DD, Claude/hooks/YYYY-MM-DD
```

`sync_claude_skills.py` syncs compact, coding/programming/documentation-scoped skill and hook
cards from the official `anthropics/claude-code` GitHub repository into:

```text
Claude/skills/YYYY-MM-DD/skills/
Claude/hooks/YYYY-MM-DD/hooks/
```

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

`SKILLS_CATALOG.yaml` and `.version` remain the flat canonical reference and are not modified by
the dated-snapshot sync; both mechanisms coexist without conflict.

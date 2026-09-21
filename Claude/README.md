# Claude Skill Routine

This directory contains Claude Code-focused skill artifacts.

The routine entrypoint is:

```bash
python scripts/sync_claude_skills.py
```

It syncs compact coding/programming/documentation skill cards from the
official [anthropics/claude-code](https://github.com/anthropics/claude-code)
CHANGELOG into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

The legacy flat catalog at `Claude/skills/SKILLS_CATALOG.yaml` is kept for
backward compatibility; it is not rewritten per skill, only its `version`
and `updated` fields are refreshed. New skills discovered by the routine are
added additively as dated snapshots instead of being merged into the flat
file, so existing consumers of `SKILLS_CATALOG.yaml` are unaffected.

Re-running the script on the same UTC date is a no-op if that date's
changelog already exists, so it is safe to invoke more than once per day.

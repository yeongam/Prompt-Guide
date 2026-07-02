# Claude Skill Sync Routine

This directory contains Claude-focused skill artifacts.

`Claude/skills/SKILLS_CATALOG.yaml` and `Claude/skills/.version` are maintained by the
existing `scripts/update_skills.py` routine (tracks the Claude Code CLI release
changelog) and are left untouched by the routine below.

The dated-snapshot routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It syncs compact skill cards (coding, programming, documentation topics) from official
Anthropic GitHub repositories into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

The dedicated GitHub Actions workflow runs this routine daily at 00:00 KST and blocks
routine changes outside `Claude/`.

Sources are read via `raw.githubusercontent.com`; each card records a content
fingerprint of the fetched README instead of a git commit SHA.

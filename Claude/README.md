# Claude Skill Sync Routine

This directory contains Claude Code-focused skill artifacts only.

The routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It syncs compact skill cards from the official `anthropics/claude-code` GitHub
repository into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

and keeps the legacy `Claude/skills/SKILLS_CATALOG.yaml` / `.version` files in
sync (version and updated-date fields only) for backward compatibility.

The `daily-skill-update.yml` GitHub Actions workflow runs this routine daily at
00:00 KST and blocks routine changes outside `Claude/`.

Skills currently tracked are limited to coding, programming, and documentation
work (`init`, `code-review`, `security-review`, `simplify`,
`session-start-hook`, `claude-api`, `document-generation`), matching the scope
of the upstream repository's own developer-facing skills.

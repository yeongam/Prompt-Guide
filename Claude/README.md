# Claude Skill Routine

This directory contains Claude Code-focused skill artifacts only.

The routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It syncs compact skill cards, sourced from the official `anthropics/claude-code`
marketplace catalog (`.claude-plugin/marketplace.json`) and `CHANGELOG.md`,
filtered to plugins in the `development`, `productivity`, and `security`
categories (coding / programming / documentation work), into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

This replaces the earlier flat `Claude/skills/SKILLS_CATALOG.yaml` /
`.version` files, which are superseded by the dated-snapshot structure
(see `Claude/Changelogs/2026-08-05.txt` for the migration note).

## Scope note

This script only reads public files from `anthropics/claude-code` over
`raw.githubusercontent.com` and only writes inside `Claude/`. It does not
touch `.claude/settings.json`, crontab, or any Stop/session hooks. A
separate, pre-existing automation path in this repo (`scripts/update_skills.py`,
`.github/workflows/daily-skill-update.yml`, `scripts/setup_local_cron.sh`,
`scripts/sync_changelogs.sh`, and permission/hook entries in
`.claude/settings.json`) installs a system crontab entry and copies files to
a local desktop path outside the repo on every session stop. That path was
intentionally left untouched here — see the changelog for details.

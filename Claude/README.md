# Claude Skill Routine

This directory contains Claude-focused skill artifacts.

`Claude/skills/SKILLS_CATALOG.yaml` and `Claude/skills/.version` track the
Claude Code CLI's own changelog/version (via `scripts/update_skills.py`,
run by `.github/workflows/daily-skill-update.yml`). That mechanism is
unchanged by this routine.

The coding/programming/documentation skill-card routine entrypoint is:

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

The dedicated GitHub Actions workflow (`.github/workflows/claude-anthropic-skills-sync.yml`)
runs this routine daily at 00:00 UTC and blocks routine changes outside `Claude/`.

If `api.github.com` is unreachable (e.g. a network-scoped session), the script
falls back to a content-hash source reference instead of a commit SHA, so it
still produces a valid snapshot.

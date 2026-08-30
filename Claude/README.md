# Claude Code Skills Routine

This directory tracks the official Claude Code (`anthropics/claude-code`) changelog and mirrors
relevant coding/programming/documentation skills for reference.

The routine entrypoint is:

```bash
python scripts/update_skills.py
```

It fetches `CHANGELOG.md` from the official repo, bumps `Claude/skills/.version`, updates the
canonical catalog at:

```text
Claude/skills/SKILLS_CATALOG.yaml
```

and writes a dated, non-destructive snapshot of the coding/programming/documentation-related
skills to:

```text
Claude/skills/YYYY-MM-DD/skills/
```

(one compact `cmd`/`trigger`/`desc` card per skill, plus a `catalog.json` index — same convention
as `GPT/skills/YYYY-MM-DD/skills/`). It also writes a changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

listing added/modified/deleted skills, structural and token-saving notes, and conflict-resolution
notes for that run, plus a "needs review" list of newly-mentioned commands/hooks/settings/env vars
detected in the changelog diff. The script never invents descriptions for items it hasn't seen a
real source line for — new items are surfaced by name only, for a human (or a future run) to fold
into `SKILLS_CATALOG.yaml` with an accurate description before they're treated as confirmed.

`SKILLS_CATALOG.yaml` remains the single source of truth; the dated snapshots are a derived,
append-only view, so re-running the script never overwrites a prior day's snapshot.

The dedicated GitHub Actions workflow (`.github/workflows/daily-skill-update.yml`) runs this
routine daily at 00:00 UTC.

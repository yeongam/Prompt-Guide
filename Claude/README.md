# Claude Skill Sync Routine

The routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It syncs compact coding/programming/documentation skill cards from the official
[anthropics/claude-code](https://github.com/anthropics/claude-code) repository into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

New skills discovered in the upstream CHANGELOG are merged into
`Claude/skills/SKILLS_CATALOG.yaml` only when their slug doesn't already exist there
(conflicts are recorded, never overwritten). It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

covering added/modified/deleted skills, structure and token-saving notes, and any
conflict resolutions.

The dedicated GitHub Actions workflow (`claude-code-skills-sync.yml`) runs this
routine daily at 00:00 KST and blocks routine changes outside `Claude/`.

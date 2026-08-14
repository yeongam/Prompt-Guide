# Claude Skill Routine

This directory contains two independent, non-overlapping catalogs:

- `Claude/skills/SKILLS_CATALOG.yaml` — Claude Code's built-in slash commands
  and hooks, kept in sync with the `anthropics/claude-code` CHANGELOG via
  `scripts/update_skills.py` (repo-root `scripts/`, unrelated to this
  directory's routine).
- `Claude/skills/YYYY-MM-DD/skills/` — dated snapshots of Agent Skill cards
  (coding, programming, and documentation skills only) sourced from the
  official [`anthropics/skills`](https://github.com/anthropics/skills)
  repository.

The dated-snapshot routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It syncs compact skill cards into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

and writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

The dedicated GitHub Actions workflow (`claude-skills-sync.yml`) runs this
routine daily at 00:00 KST and blocks routine changes outside `Claude/`.

Slugs are checked against the existing slash-command catalog to avoid
namespace collisions; any conflict is recorded in the dated changelog under
`[충돌 해결 내역]` instead of being applied silently.

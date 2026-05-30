# Team Onboarding

- Slug: `team-onboarding`
- Cmd: `/team-onboarding`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants a teammate ramp-up guide for Claude Code usage

## Procedure

1. Read CLAUDE.md, `.claude/settings.json`, recent transcripts.
2. Extract: key commands, workflow patterns, permissions granted, hooks active.
3. Generate onboarding guide as markdown.
4. Keep under 2 pages; link to deeper docs.

## Output

`ONBOARDING.md` — key commands, workflow, permissions, first-day checklist.

## Token Policy

- Bullet list format only; no verbose prose.
- Link to local docs, not copy them.
- Max 100 lines.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

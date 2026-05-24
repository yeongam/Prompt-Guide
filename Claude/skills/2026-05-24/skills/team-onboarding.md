# Team Onboarding

- Slug: `team-onboarding`
- Cmd: `/team-onboarding`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: teammate ramp-up guide, onboarding new team member

## Procedure

1. Read Claude Code usage history and transcripts.
2. Extract frequent patterns and conventions.
3. Write onboarding guide with examples.

## Output

Generate onboarding guide from local Claude Code usage history

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

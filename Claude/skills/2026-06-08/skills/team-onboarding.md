# team-onboarding

- Slug: `team-onboarding`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants teammate ramp-up guide

## Procedure

Command: `/team-onboarding`

Generate onboarding guide from local Claude Code usage history/data

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
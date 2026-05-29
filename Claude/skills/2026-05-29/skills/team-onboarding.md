# Team Onboarding

- Slug: `team-onboarding`
- Command: `/team-onboarding`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants teammate ramp-up guide

## Description

Generate onboarding guide from local Claude Code usage history

## Procedure

1. Scan Claude Code usage history.
2. Extract common patterns and commands.
3. Write onboarding guide.

## Output

Onboarding guide document.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Team Onboarding

- Slug: `team-onboarding`
- Command: `/team-onboarding`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants teammate ramp-up guide

## Procedure

1. Scan local Claude Code usage history.
2. Extract common workflows and patterns.
3. Generate structured onboarding document.

## Output

Onboarding guide from local Claude Code usage history

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

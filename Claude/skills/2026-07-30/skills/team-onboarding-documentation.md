# Team Onboarding Documentation

- Slug: `team-onboarding-documentation`
- Command: `/team-onboarding`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: User wants a teammate ramp-up guide.

## Procedure

1. Read local Claude Code usage history and data.
2. Generate an onboarding guide from observed patterns.

## Output

Onboarding guide generated from local usage history.

## Token Policy

- Avoid repeated background context; use the catalog entry instead.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve SKILLS_CATALOG.yaml as the flat canonical reference.

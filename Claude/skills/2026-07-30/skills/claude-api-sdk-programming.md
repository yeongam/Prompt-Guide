# Claude API SDK Programming

- Slug: `claude-api-sdk-programming`
- Command: `/claude-api`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: Code imports the Anthropic SDK or user asks about Claude API features.

## Procedure

1. Check model IDs and current SDK request shapes.
2. Apply prompt caching and tool-use patterns correctly.
3. Flag deprecated model IDs during migration.

## Output

Working Claude API integration or migration fix.

## Token Policy

- Avoid repeated background context; use the catalog entry instead.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve SKILLS_CATALOG.yaml as the flat canonical reference.

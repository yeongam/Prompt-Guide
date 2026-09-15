# Skill Doctor

- Slug: `skill-doctor`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: user wants to see which loaded skills go unused and their context cost

## Procedure

1. Added as `/skill-doctor`.
2. Reports unused loaded skills and their token cost so they can be pruned.

## Output

A report of loaded-skill usage and context cost.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

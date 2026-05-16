# Theme

- Slug: `theme`
- Command: `/theme [name]`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants to change or create visual theme

## Procedure

1. List available themes if no arg given.
2. Apply named theme or open creation flow.

## Output

Applied or newly created color theme

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

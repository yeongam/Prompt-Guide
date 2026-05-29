# Theme

- Slug: `theme`
- Command: `/theme [name]`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to change or create visual theme

## Description

Create or switch custom color themes

## Procedure

1. List available themes.
2. Apply or create named theme.

## Output

Theme applied confirmation.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

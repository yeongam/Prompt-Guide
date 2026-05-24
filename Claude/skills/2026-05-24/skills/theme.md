# Theme

- Slug: `theme`
- Cmd: `/theme [name]`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: change visual theme, create color theme

## Procedure

1. List available themes.
2. Apply named theme or open editor.
3. Save theme to config.

## Output

Create or switch custom color themes

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

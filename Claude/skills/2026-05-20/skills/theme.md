# Theme

- Slug: `theme`
- Cmd: `/theme [name]`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants to change or create visual theme

## Procedure

1. List available themes.
2. Apply or create requested theme.
3. Confirm change.

## Output

Theme applied or created.

## Token Policy

- Color hex values only; no design narrative.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

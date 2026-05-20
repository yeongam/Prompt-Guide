# Session Color

- Slug: `color`
- Cmd: `/color`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants a session color

## Procedure

1. Pick random color if no arg.
2. Apply to session.
3. Show hex value.

## Output

Session color set.

## Token Policy

- One-line: color name + hex.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Color

- Slug: `color`
- Cmd: `/color`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: set session color, random color

## Procedure

1. Pick random or specified color.
2. Apply to session UI.
3. Persist for session duration.

## Output

Set random session color (no args = random pick)

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

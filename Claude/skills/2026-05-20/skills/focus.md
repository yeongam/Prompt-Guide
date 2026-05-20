# Focus View

- Slug: `focus`
- Cmd: `/focus`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants compact view of conversation

## Procedure

1. Toggle focus mode.
2. Confirm current state.

## Output

Focus view toggled.

## Token Policy

- One-line confirmation.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

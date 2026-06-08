# keybindings-help

- Slug: `keybindings-help`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to remap keys or add chord shortcuts

## Procedure

Command: `/keybindings-help`

Customize ~/.claude/keybindings.json; supports chord bindings

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
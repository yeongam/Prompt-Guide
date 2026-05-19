# keybindings-help

- Slug: `keybindings-help`
- Command: `/keybindings-help`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to remap keys or add chord shortcuts

## Description

Customize ~/.claude/keybindings.json; supports chord bindings

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

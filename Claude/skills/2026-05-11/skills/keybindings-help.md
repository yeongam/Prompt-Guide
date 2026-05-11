# keybindings-help

- Cmd: `/keybindings-help`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to remap keys or add chord shortcuts

## Description

Customize ~/.claude/keybindings.json; supports chord bindings

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.

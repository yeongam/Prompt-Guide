# Keybindings Help

- Slug: `keybindings-help`
- Cmd: `/keybindings-help`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: remap keys, add chord shortcuts, customize keybindings

## Procedure

1. Show current bindings.
2. Parse user's desired binding.
3. Write updated keybindings.json entry.

## Output

Customize ~/.claude/keybindings.json; supports chord bindings

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

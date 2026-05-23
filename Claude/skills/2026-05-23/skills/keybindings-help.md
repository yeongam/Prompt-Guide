# Keybindings Help

- Slug: `keybindings-help`
- Command: `/keybindings-help`
- Source: https://github.com/anthropics/claude-code
- Trigger: User wants to remap keys or add chord shortcuts

## Procedure

1. Read current ~/.claude/keybindings.json.
2. Apply requested binding change.
3. Validate no conflicts with existing bindings.

## Output

Updated ~/.claude/keybindings.json.

## Token Policy

- Show only changed keybinding entries.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
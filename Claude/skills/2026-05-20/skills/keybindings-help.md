# Keybindings Help

- Slug: `keybindings-help`
- Cmd: `/keybindings-help`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants to remap keys or add chord shortcuts

## Procedure

1. Read current keybindings.json.
2. Identify conflicts.
3. Add or update bindings.
4. List new shortcuts.

## Output

Keybinding JSON entries to add or modify.

## Token Policy

- Emit new/changed entries only.
- Skip unchanged bindings.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

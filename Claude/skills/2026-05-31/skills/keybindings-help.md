# keybindings-help

- Slug: `keybindings-help`
- Cmd: `/keybindings-help`
- Source: https://github.com/anthropics/claude-code
- Trigger: User wants to remap keys or add chord shortcuts.

## Procedure

1. Read ~/.claude/keybindings.json.
2. Apply requested binding changes.
3. Show diff; confirm with user.

## Output

Updated keybindings.json.

## Token Policy

- Read once; patch only changed bindings.

## Compatibility

- Supports chord bindings (multi-key sequences).

# Keybindings Help

- Slug: `keybindings-help`
- Command: `/keybindings-help`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants to remap keys or add chord shortcuts

## Procedure

1. Read current ~/.claude/keybindings.json.
2. Apply requested keybinding changes.
3. Support chord bindings with array syntax.
4. Validate JSON after editing.

## Output

Updated ~/.claude/keybindings.json

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

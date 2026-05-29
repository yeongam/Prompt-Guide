# Keybindings Help

- Slug: `keybindings-help`
- Command: `/keybindings-help`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to remap keys or add chord shortcuts

## Description

Customize ~/.claude/keybindings.json; chord binding support

## Procedure

1. Read ~/.claude/keybindings.json.
2. Apply requested rebinding.
3. Validate for conflicts.

## Output

Updated keybindings.json snippet.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

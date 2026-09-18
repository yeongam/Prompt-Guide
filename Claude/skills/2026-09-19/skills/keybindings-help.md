# Keybindings Help

- Slug: `keybindings-help`
- Command: `/keybindings-help`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Customize ~/.claude/keybindings.json, including chord bindings.

## Procedure

1. Identify the current binding to change or add.
2. Write the rebind or chord to keybindings.json.
3. Confirm no existing binding conflicts.

## Output

Updated keybindings.json.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.

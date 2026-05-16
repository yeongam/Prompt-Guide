# Focus

- Slug: `focus`
- Command: `/focus`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants compact view of conversation

## Procedure

1. Toggle focus mode.
2. Hides intermediate tool output from display.

## Output

Compact view: prompt + tool summary + final response only

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

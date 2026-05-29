# Focus

- Slug: `focus`
- Command: `/focus`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants compact view of conversation

## Description

Toggle focus view: prompt + tool summary + final response only

## Procedure

1. Toggle focus mode.
2. Show compact view.

## Output

Focus mode state toggled.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

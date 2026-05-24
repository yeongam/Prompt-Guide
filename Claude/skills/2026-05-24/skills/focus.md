# Focus

- Slug: `focus`
- Cmd: `/focus`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: compact view, hide tool calls, clean output

## Procedure

1. Toggle focus mode.
2. Collapse intermediate tool output.
3. Show only essential turn content.

## Output

Toggle focus view: prompt + tool summary + final response only

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

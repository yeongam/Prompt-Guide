# effort

- Cmd: `/effort`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: user wants to adjust effort/quality level

## Description

Interactive slider for session effort level (also: CLAUDE_EFFORT env var)

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

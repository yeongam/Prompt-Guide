# run

- Cmd: `/run`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: user asks to run, start, or screenshot the app

## Description

Launch and drive project app; confirms change works in real app (not just tests)

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

# statusline-setup

- Cmd: `/statusline-setup`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: user wants to configure Claude Code status line

## Description

Configure the Claude Code status line setting in settings.json

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

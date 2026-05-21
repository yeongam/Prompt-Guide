# tui

- Cmd: `/tui`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: rendering looks flickery or user wants full-screen mode

## Description

Switch to flicker-free alt-screen TUI rendering (also: CLAUDE_CODE_NO_FLICKER)

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

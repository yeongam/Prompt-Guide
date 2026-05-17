# tui

- Cmd: `/tui`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: rendering looks flickery or user wants full-screen mode

## Description

Switch to flicker-free alt-screen TUI rendering (also: CLAUDE_CODE_NO_FLICKER)

## Token Policy

- Return only decision-critical output.
- Link to source repo instead of copying long docs.
- Avoid repeating context already in the prompt.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

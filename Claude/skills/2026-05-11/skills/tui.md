# tui

- Cmd: `/tui`
- Source: https://github.com/anthropics/claude-code
- Trigger: rendering looks flickery or user wants full-screen mode

## Description

Switch to flicker-free alt-screen TUI rendering (also: CLAUDE_CODE_NO_FLICKER)

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.

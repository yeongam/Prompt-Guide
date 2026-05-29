# TUI

- Slug: `tui`
- Command: `/tui`
- Source: https://github.com/anthropics/claude-code
- Trigger: rendering looks flickery or user wants full-screen mode

## Description

Switch to flicker-free alt-screen TUI rendering

## Procedure

1. Toggle alt-screen rendering.
2. Equivalent: CLAUDE_CODE_NO_FLICKER=1

## Output

TUI mode activated.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

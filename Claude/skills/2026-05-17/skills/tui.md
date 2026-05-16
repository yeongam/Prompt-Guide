# TUI

- Slug: `tui`
- Command: `/tui`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: Rendering looks flickery or user wants full-screen mode

## Procedure

1. Toggle alt-screen TUI mode.
2. Equivalent to CLAUDE_CODE_NO_FLICKER=1 env var.

## Output

Alt-screen flicker-free TUI rendering

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

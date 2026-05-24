# TUI

- Slug: `tui`
- Cmd: `/tui`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: flickery rendering, full-screen mode, alt-screen

## Procedure

1. Toggle alt-screen mode.
2. Redraw UI cleanly.
3. Persist preference to session.

## Output

Switch to flicker-free alt-screen TUI rendering

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

**Note:** Also: CLAUDE_CODE_NO_FLICKER=1

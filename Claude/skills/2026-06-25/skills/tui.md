# tui

**cmd:** `/tui`
**trigger:** rendering looks flickery or user wants full-screen mode
**desc:** Switch to flicker-free alt-screen TUI rendering (also: CLAUDE_CODE_NO_FLICKER)

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.
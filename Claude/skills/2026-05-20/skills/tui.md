# TUI Mode

- Slug: `tui`
- Cmd: `/tui`
- Source: anthropics/claude-code v2.1.145
- Trigger: rendering looks flickery or user wants full-screen mode

## Procedure

1. Toggle CLAUDE_CODE_NO_FLICKER.
2. Restart rendering context.
3. Confirm flicker-free state.

## Output

TUI mode activated.

## Token Policy

- Confirmation only; no setup narrative.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

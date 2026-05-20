# Effort Level

- Slug: `effort`
- Cmd: `/effort`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants to adjust effort/quality level

## Procedure

1. Show current level.
2. Accept new level (1-5).
3. Set CLAUDE_EFFORT.
4. Confirm effect on response depth.

## Output

Effort level confirmed; CLAUDE_EFFORT set.

## Token Policy

- Emit only level change confirmation.
- No explanation of levels unless asked.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Effort

- Slug: `effort`
- Cmd: `/effort`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: adjust effort level, quality level, speed vs depth

## Procedure

1. Show current effort level.
2. Accept slider input or named level.
3. Apply to session context window strategy.

## Output

Interactive effort slider for session (also: CLAUDE_EFFORT env var)

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

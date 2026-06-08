# effort

- Slug: `effort`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to adjust effort/quality level

## Procedure

Command: `/effort`

Interactive slider for session effort level (also: CLAUDE_EFFORT env var)

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
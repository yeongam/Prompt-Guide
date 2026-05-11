# effort

- Cmd: `/effort`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to adjust effort/quality level

## Description

Interactive slider for session effort level (also: CLAUDE_EFFORT env var)

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.

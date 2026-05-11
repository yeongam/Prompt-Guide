# theme

- Cmd: `/theme [name]`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to change or create visual theme

## Description

Create or switch custom color themes

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.

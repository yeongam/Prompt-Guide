# usage

- Cmd: `/usage`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks about token or cost statistics

## Description

Show token usage and cost stats (merged /cost + /stats)

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.

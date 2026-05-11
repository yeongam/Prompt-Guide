# review

- Cmd: `/review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to review PR or branch

## Description

Multi-pass PR review; checks logic, style, security, tests

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.

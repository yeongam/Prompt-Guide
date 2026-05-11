# security-review

- Cmd: `/security-review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks security audit of current branch changes

## Description

OWASP-focused audit of pending diffs; outputs risk-ranked findings

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.

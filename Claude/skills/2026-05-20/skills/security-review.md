# security-review

- Slug: `security-review`
- Command: `/security-review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks security audit of current branch changes

## Description

OWASP-focused audit of pending diffs; outputs risk-ranked findings

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

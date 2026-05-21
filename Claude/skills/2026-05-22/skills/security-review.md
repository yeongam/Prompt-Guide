# security-review

- Cmd: `/security-review`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: user asks security audit of current branch changes

## Description

OWASP-focused audit of pending diffs; outputs risk-ranked findings

## Token Policy

- Report only non-trivial findings.
- Rank by severity to front-load critical items.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

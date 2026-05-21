# review

- Cmd: `/review`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: user asks to review PR or branch

## Description

Multi-pass PR review; checks logic, style, security, tests

## Token Policy

- Cap raw diff output; summarise per-file.
- Stop after first full pass unless issues found.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

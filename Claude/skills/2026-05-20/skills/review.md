# review

- Slug: `review`
- Command: `/review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to review PR or branch

## Description

Multi-pass PR review; checks logic, style, security, tests

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

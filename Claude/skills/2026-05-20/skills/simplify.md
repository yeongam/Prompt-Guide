# simplify

- Slug: `simplify`
- Command: `/simplify`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to clean up or refactor changed code

## Description

Review changed code for reuse/quality/efficiency, then fix issues

## Token Policy

- Return only decision-critical output.
- Avoid repeated background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

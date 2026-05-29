# Verify

- Slug: `verify`
- Command: `/verify`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to verify a PR or confirm a fix works

## Description

Run app, exercise change path, confirm correct behavior

## Procedure

1. Launch app via /run.
2. Exercise the changed feature path.
3. Note any regressions.

## Output

Verification result with observed behavior.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

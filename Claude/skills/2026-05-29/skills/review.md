# Review

- Slug: `review`
- Command: `/review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to review PR or branch

## Description

Multi-pass PR review: logic, style, security, tests

## Procedure

1. Read diff holistically.
2. Check logic, edge cases, test coverage.
3. Flag OWASP Top 10 issues.
4. Note style/naming deviations.

## Output

Risk-ranked findings with file:line refs.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

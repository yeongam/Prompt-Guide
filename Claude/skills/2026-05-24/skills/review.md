# Review

- Slug: `review`
- Cmd: `/review`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: review PR or branch

## Procedure

1. Diff current branch against base.
2. Check logic, edge cases, security, test coverage.
3. Output risk-ranked findings with line references.

## Output

Multi-pass PR review; logic, style, security, tests

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

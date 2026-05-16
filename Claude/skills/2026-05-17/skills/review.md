# Review

- Slug: `review`
- Command: `/review`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User asks to review a PR or branch

## Procedure

1. Read diff and recent commits.
2. Check logic errors, edge cases, and security issues.
3. Verify test coverage matches changed paths.
4. Output risk-ranked findings with file:line references.

## Output

Multi-pass review: logic, style, security, tests

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

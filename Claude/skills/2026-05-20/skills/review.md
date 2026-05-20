# PR Review

- Slug: `review`
- Cmd: `/review`
- Source: anthropics/claude-code v2.1.145
- Trigger: user asks to review PR or branch

## Procedure

1. Fetch diff.
2. Check logic correctness.
3. Check style and naming.
4. Check security (OWASP Top 10).
5. Check test coverage.

## Output

Ranked findings with severity and fix suggestions.

## Token Policy

- Return findings only, not unchanged lines.
- Group by severity.
- Link to line numbers.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Code Review

- Slug: `code-review`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.187`
- Trigger: user asks to review PR, branch diff, or check code quality

## Procedure

1. Read changed files before reviewing.
2. Check logic, style, security, and test coverage.
3. Rank findings by severity.
4. Keep review concise; link to docs for known patterns.
5. Verify fixes narrow to reported issues only.

## Output

Risk-ranked finding list with severity and fix suggestions.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical findings.
- Skip trivial style notes when higher issues exist.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

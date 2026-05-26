# Review

- Slug: `review`
- Source: https://github.com/anthropics/claude-code
- Catalog version: `2.1.129`
- Trigger: user asks to review PR or branch

## Procedure

1. Read changed files and diff.
2. Check logic correctness, edge cases, error handling.
3. Check style consistency with repo conventions.
4. Flag security issues (OWASP top 10).
5. Verify test coverage for changed paths.

## Output

Ranked findings list with file:line references.

## Token Policy

- Skip findings with no actionable fix.
- Group related issues under one finding.
- Cap output at 20 findings; note if truncated.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

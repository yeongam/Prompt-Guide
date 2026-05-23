# PR Review

- Slug: `review`
- Command: `/review`
- Source: https://github.com/anthropics/claude-code
- Trigger: User asks to review PR or branch diff

## Procedure

1. Read full diff; identify changed files.
2. Check logic correctness, edge cases, error handling.
3. Check style consistency with codebase.
4. Check security implications (input validation, auth, injection).
5. Check test coverage for changed paths.
6. Output ranked findings: Critical → High → Medium → Low.

## Output

Ranked review findings with file:line references.

## Token Policy

- One finding per line; no padding prose.
- Skip findings below Low severity unless explicitly requested.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
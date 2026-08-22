# Code Review

- Slug: `code-review`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source commit: `5cfc0a1905ce`
- Source version: 2.1.240
- Trigger: User asks to review a PR, branch, or diff.

## Procedure

1. Diff the target against its base and read changed files in full.
2. Check logic correctness, style consistency, and test coverage.
3. Rank findings by severity; verify each before reporting.
4. Report only confirmed, actionable findings.

## Output

Ranked review findings with file:line references.

## Token Policy

- No repeated background context across turns.
- Return decision-critical output only.
- Reference the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

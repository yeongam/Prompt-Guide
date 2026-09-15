# Code Review

- Slug: `code-review`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: review a diff, PR number, branch, or path for bugs and cleanup

## Procedure

1. Renamed from /review; reports correctness bugs at a chosen effort level.
2. Also surfaces reuse/simplification/efficiency cleanups.
3. --comment posts inline PR comments; --fix applies findings to the working tree.

## Output

Ranked findings, optionally posted as PR comments or auto-fixed.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

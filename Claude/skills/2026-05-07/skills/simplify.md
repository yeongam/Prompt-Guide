# Simplify (Code Quality)

- Slug   : `simplify`
- Source : https://github.com/anthropics/claude-code
- Version: 2.1.129
- Trigger: user asks to clean up or refactor changed code

## Procedure

1. Review changed files only.
2. Remove dead code and redundancy.
3. Inline single-use helpers.
4. Fix issues in-place.

## Output

Compact, issue-free version of changed code.

## Token Policy

- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

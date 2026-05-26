# Simplify

- Slug: `simplify`
- Source: https://github.com/anthropics/claude-code
- Catalog version: `2.1.129`
- Trigger: user asks to clean up or refactor changed code

## Procedure

1. Identify duplicate logic across changed files.
2. Extract reusable helpers where 3+ repetitions exist.
3. Remove dead code and unused imports.
4. Apply consistent naming conventions.

## Output

Refactored code diff with explanation.

## Token Policy

- Don't add comments explaining the refactor.
- Return only the changed hunks.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

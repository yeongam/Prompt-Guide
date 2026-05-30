# Simplify

- Slug: `simplify`
- Cmd: `/simplify`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to clean up or refactor changed code

## Procedure

1. Diff changed files only.
2. Find: duplicate logic, unnecessary abstractions, inefficient calls, dead code.
3. Apply fixes directly to working tree.
4. Run tests if available to confirm no regression.
5. Report diff summary.

## Output

Applied fixes in-place; diff summary (files changed, lines ±).

## Token Policy

- Apply without asking unless change is architectural.
- Return diff summary only, not full file.
- Quality improvements only — bugs go to `/code-review`.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

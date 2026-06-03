# Simplify

- Slug: `simplify`
- Cmd: `/simplify`
- Source: https://github.com/anthropics/claude-code
- Source branch: `main`
- Catalog version: `2.1.161`
- Trigger: user asks to clean up or refactor changed code; quality review without bug hunting

## Procedure

1. Review changed code only, not full repo.
2. Check for: reuse, simplification, efficiency, altitude cleanups.
3. Apply fixes directly.
4. Do not hunt for bugs; use /code-review for that.
5. No half-finished refactors.

## Output

Cleaned diff with concise summary of each simplification applied.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Simplify

- Slug: `simplify`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: user asks to clean up or refactor already-changed code

## Procedure

1. Cleanup-only pass: reuse, simplification, efficiency, altitude.
2. Applies fixes directly; does not hunt for correctness bugs (use code-review).

## Output

Working tree with cleanup fixes applied.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Code Simplify & Refactor

- Slug: `code-simplify-refactor`
- Command: `/simplify`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: User asks to clean up or refactor changed code.

## Procedure

1. Review changed code for reuse, quality, efficiency.
2. Apply fixes directly; skip bug-hunting (use /review).

## Output

Simplified diff with reuse/efficiency issues fixed.

## Token Policy

- Avoid repeated background context; use the catalog entry instead.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve SKILLS_CATALOG.yaml as the flat canonical reference.

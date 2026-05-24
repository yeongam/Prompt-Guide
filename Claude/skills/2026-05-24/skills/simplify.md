# Simplify

- Slug: `simplify`
- Cmd: `/simplify`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: clean up or refactor changed code

## Procedure

1. Identify duplication, dead code, and complexity.
2. Propose minimal refactor.
3. Apply changes preserving behavior.

## Output

Review changed code for reuse/quality/efficiency then fix

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Simplify Code

- Slug: `simplify`
- Cmd: `/simplify`
- Source: anthropics/claude-code v2.1.145
- Trigger: user asks to clean up or refactor changed code

## Procedure

1. Identify duplication.
2. Apply DRY where safe.
3. Remove dead code.
4. Verify tests still pass.

## Output

Refactored diff with one-line rationale per change.

## Token Policy

- Show diff only, not full file.
- One-line rationale per change.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

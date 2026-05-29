# Simplify

- Slug: `simplify`
- Command: `/simplify`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to clean up or refactor changed code

## Description

Review changed code for reuse/quality/efficiency; apply fixes

## Procedure

1. Read changed files only.
2. Identify duplication, dead code, unnecessary abstractions.
3. Apply minimal cleanup — no speculative refactors.

## Output

Cleaned diff with one-line rationale per change.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

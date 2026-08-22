# Simplify

- Slug: `simplify`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source commit: `5cfc0a1905ce`
- Source version: 2.1.240
- Trigger: User asks to clean up, refactor, or simplify changed code.

## Procedure

1. Review changed code for reuse, redundancy, and unneeded abstraction.
2. Prefer deletion over addition when removing complexity.
3. Apply fixes directly rather than only reporting them.
4. Leave working behavior unchanged.

## Output

Simplified code with quality fixes applied in place.

## Token Policy

- No repeated background context across turns.
- Return decision-critical output only.
- Reference the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

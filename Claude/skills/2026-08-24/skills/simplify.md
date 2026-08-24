# Simplify

- Slug: `simplify`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: user asks to clean up or refactor recently changed code

## Procedure

1. Review changed code only, not the whole codebase.
2. Look for reuse, simplification, and efficiency opportunities.
3. Apply the fixes directly; does not hunt for correctness bugs.

## Output

Simplified diff with quality cleanups applied.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

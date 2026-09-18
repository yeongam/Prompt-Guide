# Simplify

- Slug: `simplify`
- Command: `/simplify`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Clean up changed code for reuse, simplification, and efficiency only.

## Procedure

1. Read only the changed hunks, not the whole file.
2. Find duplication, dead abstractions, and inefficient patterns.
3. Apply the fix directly; do not report a separate findings list.

## Output

Directly-applied quality fixes to the diff.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.

# Simplify

- Slug: `simplify`
- Command: `/simplify`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User asks to clean up or refactor changed code

## Procedure

1. Identify duplicate logic and dead code in changed files.
2. Remove unnecessary abstractions.
3. Prefer standard library over custom implementations.
4. Verify behavior is unchanged after simplification.

## Output

Refactored code with explanation of changes

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

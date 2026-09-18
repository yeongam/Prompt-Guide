# Code Review

- Slug: `code-review`
- Command: `/code-review`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Review a diff, PR, branch, or path for correctness bugs and cleanups.

## Procedure

1. Scope the diff or target (PR/branch/path/effort level).
2. Check correctness first; reuse/simplify/efficiency where in scope.
3. Rank findings by confidence; low/medium = fewer, high-confidence only.
4. Optionally post inline PR comments or apply fixes directly.

## Output

Ranked findings list, or applied fixes with --fix.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.

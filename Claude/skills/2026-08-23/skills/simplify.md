# Simplify

- Slug: `simplify`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: User asks to clean up, simplify, or refactor changed code (quality only, not bug-hunting).

## Procedure

1. Review the changed code for reuse, simplification, efficiency, and "altitude" cleanups.
2. Prefer the smallest working change; no premature abstractions.
3. Apply the fixes directly rather than only reporting them.

## Output

Cleaned-up diff with no behavior change and no new bugs introduced.

## Token Policy

- Reuse the canonical entry in `Claude/skills/SKILLS_CATALOG.yaml` instead of duplicating it here.

## Compatibility

- Complements `/code-review` (which hunts bugs); `/simplify` does not — keep the two separate.
- Do not overwrite existing dated skill snapshots; integrate only if content changed.

## Source Summary

Official Claude Code skill: reviews changed code for reuse/simplification/efficiency and applies the fixes. No changelog-visible behavior change between v2.1.129 and v2.1.241.

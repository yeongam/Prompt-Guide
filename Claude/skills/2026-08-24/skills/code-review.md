# Code Review

- Slug: `code-review`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: user asks to review the current diff, a PR, branch, or path

## Procedure

1. Scope the diff or target (PR/branch/path) at the requested effort level.
2. Check correctness bugs first, then reuse/simplification/efficiency.
3. Rank findings by confidence; broaden coverage only at high effort.

## Output

Ranked findings, optionally posted as inline PR comments or auto-fixed.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

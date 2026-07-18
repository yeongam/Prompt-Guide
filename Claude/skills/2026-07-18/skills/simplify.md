# /simplify

- Slug: `simplify`
- Command: `/simplify`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user asks to clean up or refactor changed code

## Description

Review changed code for reuse/quality/efficiency, then fix issues

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

`/simplify` now runs a cleanup-only review (reuse, simplification, efficiency, altitude)
and applies the fixes, instead of running the full `/code-review --fix` bug-hunting
review

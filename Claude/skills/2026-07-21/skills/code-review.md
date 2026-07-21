# Code Review

- Slug: `code-review`
- Command: `/code-review`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.216`
- Trigger: user wants a correctness/bug pass over pending changes, at a chosen effort level

## Procedure

1. Diff the pending changes against the base ref.
2. Run the bug-hunting review at the requested effort level.
3. Rank findings by severity; verify each before reporting.
4. With --comment, post findings as inline GitHub PR comments.

## Output

Severity-ranked correctness findings for the current diff.

## Token Policy

- Avoid repeated background context; return only decision-critical output.
- Link to the official repo instead of copying changelog prose.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate into Claude/skills/SKILLS_CATALOG.yaml only if slug is new or hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Renamed from /simplify; now reports correctness bugs at a chosen effort level (e.g. `/code-review high`). /review <pr> reuses this engine for a fast single-pass PR review.

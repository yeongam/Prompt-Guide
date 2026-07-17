# Review (corrected)

- Slug: `review`
- Command: `/review [pr]`
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md)
- Source version: `2.1.212`
- Trigger: user asks to review a GitHub PR or branch

## Summary

`/review` is the **fast, single-pass** PR review. The catalog previously
described it as the multi-pass logic/style/security/tests reviewer — that
description now belongs to `/code-review`. This card corrects that entry.

## Conflict resolution

- Old catalog text: "Multi-pass PR review; checks logic, style, security, tests" — stale, described `/code-review`'s current behavior instead.
- Resolved: `review` → fast single-pass; `code-review` → multi-pass, effort-tunable. Both entries updated in `SKILLS_CATALOG.yaml` in this sync.

## Token Policy

- No new content beyond the corrected one-line description in the catalog.

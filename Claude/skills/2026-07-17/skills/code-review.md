# Code Review

- Slug: `code-review`
- Command: `/code-review [effort] [pr#]`
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md)
- Source version: `2.1.212`
- Trigger: user asks to review the current diff/branch for correctness bugs, or wants a multi-agent review of a PR

## Summary

Multi-pass review of the working diff (or a given PR) for correctness bugs and
reuse/simplification/efficiency cleanups, at a chosen effort level (low/medium:
fewer, high-confidence findings; high→max: broader coverage, may include
uncertain findings). `--comment` posts findings as inline PR comments;
`--fix` applies the findings to the working tree after review.

## History note

Named `/simplify` before 2.1.147 (cleanup-and-fix only); briefly merged into
one command, then re-split so `/simplify` stays cleanup-only and `/code-review`
owns correctness-bug finding. `/review` remains the fast single-pass PR review;
`/code-review` is the deeper, effort-tunable one.

## Token Policy

- Reference this card and the SKILLS_CATALOG.yaml entry; do not restate on every invocation.
- Keep findings output structured (file:line + one-sentence defect), not prose.

## Compatibility

- Does not replace `/review` (PR-only, single-pass) or `/simplify` (cleanup-only, no bug hunting).
- Existing catalog `review` entry corrected in this sync — see Changelogs/2026-07-17.txt.

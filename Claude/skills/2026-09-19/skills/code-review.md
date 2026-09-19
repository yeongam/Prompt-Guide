# Code Review

- Slug: `code-review`
- Cmd: `/code-review [level] [pr#]` (`/review` is now an alias)
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md, v2.1.278)
- Trigger: user asks to review the current diff, a PR, or a branch.

## Procedure

1. Reuse the effort level from the last invocation if none given.
2. Report correctness bugs first; reuse/simplification/efficiency only where the recipe covers them.
3. `--comment` posts findings inline on the PR (GitHub and GitLab).
4. `ultra` level runs a deep, multi-agent cloud review.

## Token Policy

- No duplicated prose; this card only tracks what changed vs. the prior catalog entry.

## Compatibility

- Do not modify GPT or Gemini directories.
- Supersedes the old `review` entry; does not remove it (kept as alias note).

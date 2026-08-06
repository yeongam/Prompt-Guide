# Code Review

- Slug: `code-review`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.223`
- Command: `/code-review [level] [pr#]`
- Trigger: user asks to review the current diff or a PR

## Output

Multi-pass review: logic, style, security, tests. `/review` is now an alias.

## Notes

- Renamed from /review; reuses last-typed effort level; `ultra` runs a deep cloud review.

## Token Policy

- One-line trigger and output; no upstream docs copied.
- Reference CHANGELOG version instead of restating history.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Do not modify GPT or Gemini directories.

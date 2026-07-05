# Review

- Slug: `review`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user asks to review a PR or branch

## Procedure

1. Confirm the current SKILLS_CATALOG.yaml entry before acting.
2. Prefer the smallest working change for the request.
3. Reuse repo conventions instead of introducing new patterns.
4. Keep prompts and tool calls short.
5. Verify with the narrowest relevant check (test, lint, or diff review).

## Output

Multi-pass review covering logic, style, security, tests.

## Token Policy

- Reference SKILLS_CATALOG.yaml instead of restating its content.
- Return only decision-critical output.
- Avoid duplicating upstream documentation text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Merge into SKILLS_CATALOG.yaml only when the slug is new or content changed.
- Preserve GPT and Gemini directories untouched.

## Source Summary

Multi-pass review covering logic, style, security, tests.

# Claude API

- Slug: `claude-api`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: code imports the Claude/Anthropic SDK

## Procedure

1. Confirm the current SKILLS_CATALOG.yaml entry before acting.
2. Prefer the smallest working change for the request.
3. Reuse repo conventions instead of introducing new patterns.
4. Keep prompts and tool calls short.
5. Verify with the narrowest relevant check (test, lint, or diff review).

## Output

Build/debug Claude API usage: caching, tool use, model choice.

## Token Policy

- Reference SKILLS_CATALOG.yaml instead of restating its content.
- Return only decision-critical output.
- Avoid duplicating upstream documentation text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Merge into SKILLS_CATALOG.yaml only when the slug is new or content changed.
- Preserve GPT and Gemini directories untouched.

## Source Summary

Build/debug Claude API usage: caching, tool use, model choice.

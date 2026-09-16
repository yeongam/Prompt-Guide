# Claude API Coding

- Slug: `claude-api-coding`
- Source: https://github.com/anthropics/claude-cookbooks
- Source ref: main (fetched 2026-09-16)
- Trigger: Use for implementing or debugging Claude API calls and examples.

## Procedure

1. Check the official source for the current API/CLI shape before coding.
2. Prefer the smallest working implementation over speculative abstractions.
3. Use the SDK's structured types/tools instead of hand-rolled parsing.
4. Keep generated snippets short; link back to the source repo for depth.
5. Verify with the narrowest relevant command or test before finishing.

## Output

Small code-oriented checklist aligned with official Claude cookbook examples.

## Token Policy

- Avoid repeating background context already in the source repo.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs verbatim.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content changed.
- Preserve changelog evidence for every generated update.

## Source Summary

> # Claude Cookbooks The Claude Cookbooks provide code and guides designed to help developers build with Claude, offering copy-able code snippets that you can easily integrate into your own projects. ## Prerequisites To make the most of the examples in this cookbook, you'll need a Claude API key (sign up for free [here](https://www.anthropic.com)). While the code examples are primarily written in Python, the concepts.

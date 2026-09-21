# Code Review

- Command: `/code-review [PR#|branch|path] [--comment] [--fix]`
- Slug: `code-review`
- Source: https://github.com/anthropics/claude-code
- Since: `2.1.218`
- Trigger: user asks to review the current diff, a PR, or a branch

## Procedure

1. Review the diff for correctness bugs plus reuse/simplification/efficiency cleanups.
2. Runs as a background subagent since 2.1.218 so it no longer fills the conversation.
3. Report findings ranked by confidence; --comment posts inline, --fix applies them.

## Output

Ranked findings list, optionally posted as PR comments or auto-fixed.

## Token Policy

- One canonical card per skill; no duplicated background context.
- Procedure capped at three steps; link to source instead of copying docs.

## Compatibility

- Additive only: does not modify or remove existing flat-catalog entries.
- Does not touch GPT/ or Gemini/ directories.

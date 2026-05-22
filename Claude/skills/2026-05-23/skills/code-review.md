# Code Review

- Slug: `code-review`
- Command: `/code-review`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user wants inline code review at a given effort level

## Description

Review diff for correctness bugs; post as inline PR comments with --comment

## Procedure

1. Confirm trigger matches user intent before invoking.
2. Prefer narrowest effective invocation.
3. Return only decision-critical output.
4. Link to source instead of copying long docs.
5. Verify result; do not narrate internal steps.

## Token Policy

- No repeated background context across calls.
- Cap skill output to what the task requires.
- Prefer YAML/JSON catalog references over inline prose.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

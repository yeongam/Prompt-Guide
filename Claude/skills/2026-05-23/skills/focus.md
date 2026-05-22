# Focus

- Slug: `focus`
- Command: `/focus`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user wants compact view of conversation

## Description

Toggle focus view showing only: prompt + tool summary + final response

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

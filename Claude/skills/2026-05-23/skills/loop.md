# Loop

- Slug: `loop`
- Command: `/loop [interval] [/command]`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Trigger: user wants recurring task (e.g. "check every 5m", "keep running X")

## Description

Run prompt or slash command on recurring interval (default 10m)

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

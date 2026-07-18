# /loop

- Slug: `loop`
- Command: `/loop [interval] [/command]`
- Category: ops
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user wants recurring task (e.g. "check every 5m")

## Description

Run prompt or slash command on recurring interval (default 10m)

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Fixed `/loop` hiding the session from `/resume` after a single use

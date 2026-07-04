# /loop [interval] [/command]

- Slug: `loop`
- Category: productivity
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md @ 2.1.201)
- Trigger: user wants a recurring task (e.g. "check every 5m")

## Description

Run a prompt or slash command on a recurring interval (default 10m)

## Token Policy

- One-line trigger/desc only; no upstream prose duplication.
- Full behavior detail lives in the skill's own SKILL.md, not this catalog.

## Compatibility

- Do not overwrite prior dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

# /update-config

- Slug: `update-config`
- Category: programming
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md @ 2.1.201)
- Trigger: automated behavior requests ("when X", "allow Y", "set Z=val")

## Description

Configure settings.json: hooks, permissions, env vars

## Token Policy

- One-line trigger/desc only; no upstream prose duplication.
- Full behavior detail lives in the skill's own SKILL.md, not this catalog.

## Compatibility

- Do not overwrite prior dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

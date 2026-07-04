# /goal

- Slug: `goal`
- Category: productivity
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md @ 2.1.201)
- Trigger: user wants Claude to keep working until a condition holds
- Changed in: 2.1.130-2.1.201

## Description

Set a completion condition; Claude keeps working across turns until it's met, with a live elapsed/turns/tokens overlay

## Token Policy

- One-line trigger/desc only; no upstream prose duplication.
- Full behavior detail lives in the skill's own SKILL.md, not this catalog.

## Compatibility

- Do not overwrite prior dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

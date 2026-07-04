# /reload-skills

- Slug: `reload-skills`
- Category: programming
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md @ 2.1.201)
- Trigger: skill files changed on disk mid-session
- Changed in: 2.1.130-2.1.201

## Description

Re-scan skill directories without restarting the session

## Token Policy

- One-line trigger/desc only; no upstream prose duplication.
- Full behavior detail lives in the skill's own SKILL.md, not this catalog.

## Compatibility

- Do not overwrite prior dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

# /simplify

- Slug: `simplify`
- Category: coding
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md @ 2.1.201)
- Trigger: user asks to clean up or refactor changed code
- Changed in: 2.1.130-2.1.201

## Description

Cleanup-only review (reuse, simplification, efficiency, altitude); now invokes /code-review --fix instead of running its own bug-hunting pass

## Token Policy

- One-line trigger/desc only; no upstream prose duplication.
- Full behavior detail lives in the skill's own SKILL.md, not this catalog.

## Compatibility

- Do not overwrite prior dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

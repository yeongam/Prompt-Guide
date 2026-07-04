# /session-start-hook

- Slug: `session-start-hook`
- Category: programming
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md @ 2.1.201)
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Description

Create a SessionStart hook that ensures the project can run tests and linters

## Token Policy

- One-line trigger/desc only; no upstream prose duplication.
- Full behavior detail lives in the skill's own SKILL.md, not this catalog.

## Compatibility

- Do not overwrite prior dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

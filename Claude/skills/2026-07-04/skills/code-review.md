# /code-review [effort] [--comment|--fix]

- Slug: `code-review`
- Category: coding
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md @ 2.1.201)
- Trigger: user asks for a bug-focused review of the current diff
- Changed in: 2.1.130-2.1.201

## Description

Reports correctness bugs at a chosen effort level; --comment posts inline PR comments, --fix applies findings to the working tree. Replaced /simplify's old bug-hunting role; five cleanup finders were merged into one (~25% fewer tokens)

## Token Policy

- One-line trigger/desc only; no upstream prose duplication.
- Full behavior detail lives in the skill's own SKILL.md, not this catalog.

## Compatibility

- Do not overwrite prior dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

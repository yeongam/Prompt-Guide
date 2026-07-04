# /security-review

- Slug: `security-review`
- Category: coding
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md @ 2.1.201)
- Trigger: user asks for a security audit of current branch changes

## Description

OWASP-focused audit of pending diffs; outputs risk-ranked findings

## Token Policy

- One-line trigger/desc only; no upstream prose duplication.
- Full behavior detail lives in the skill's own SKILL.md, not this catalog.

## Compatibility

- Do not overwrite prior dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

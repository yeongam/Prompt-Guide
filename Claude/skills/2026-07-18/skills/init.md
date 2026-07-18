# /init

- Slug: `init`
- Command: `/init`
- Category: docs
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user asks to initialize or document codebase

## Description

Generate CLAUDE.md with codebase architecture, conventions, commands

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

The model can now discover and invoke built-in slash commands like `/init`, `/review`,
and `/security-review` via the Skill tool

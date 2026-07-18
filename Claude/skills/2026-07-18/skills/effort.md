# /effort

- Slug: `effort`
- Command: `/effort`
- Category: ops
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user wants to adjust effort/quality level

## Description

Interactive slider for session effort level (also: CLAUDE_EFFORT env var)

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Fixed settings changes (such as `/effort` or `/model`) failing with ENOENT when
`~/.claude/settings.json` is a relative symlink under a symlinked `~/.claude`

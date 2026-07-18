# /cd

- Slug: `cd`
- Command: `/cd`
- Category: ops
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user wants to change the session's working directory mid-session

## Description

Move a session to a new working directory without breaking the prompt cache

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Added directory path suggestions to `/cd`, matching `/add-dir` behavior

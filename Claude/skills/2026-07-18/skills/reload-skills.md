# /reload-skills

- Slug: `reload-skills`
- Command: `/reload-skills`
- Category: ops
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user edited a skill file and wants it picked up without restarting

## Description

Re-scan skill directories without restarting the session

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Added `/reload-skills` command to re-scan skill directories without restarting the
session

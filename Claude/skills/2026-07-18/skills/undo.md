# /undo

- Slug: `undo`
- Command: `/undo`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user wants to undo last action

## Description

Alias for /rewind; undoes last assistant action

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

`/undo` is now an alias for `/rewind`

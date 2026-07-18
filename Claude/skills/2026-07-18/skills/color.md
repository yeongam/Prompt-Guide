# /color

- Slug: `color`
- Command: `/color`
- Category: ux
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user wants a session color

## Description

Set random session color (no args = random pick)

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Fixed backgrounding a session with `←` or `/background` dropping its `/color` from the
agent view row

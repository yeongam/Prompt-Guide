# /theme

- Slug: `theme`
- Command: `/theme [name]`
- Category: ux
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user wants to change or create visual theme

## Description

Create or switch custom color themes

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Fixed `/theme` "New custom theme" and color editor dialogs not responding to Esc

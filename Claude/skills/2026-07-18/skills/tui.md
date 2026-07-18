# /tui

- Slug: `tui`
- Command: `/tui`
- Category: ux
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: rendering looks flickery or user wants full-screen mode

## Description

Switch to flicker-free alt-screen TUI rendering (also: CLAUDE_CODE_NO_FLICKER)

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Fixed channel connections dropping after navigating to the agents view and back, and
after `/bg`, `/tui`, or `/update`

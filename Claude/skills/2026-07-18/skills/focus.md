# /focus

- Slug: `focus`
- Command: `/focus`
- Category: ux
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user wants compact view of conversation

## Description

Toggle focus view showing only: prompt + tool summary + final response

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Fixed `/focus` showing "Unknown command" when the fullscreen renderer is off — now
explains how to enable it

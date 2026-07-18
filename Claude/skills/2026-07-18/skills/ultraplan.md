# /ultraplan

- Slug: `ultraplan`
- Command: `/ultraplan`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user wants cloud environment for complex planning

## Description

Auto-create cloud worktrees/environments for multi-agent planning tasks

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Fixed `/ultraplan` and remote session creation failing with "Could not capture
uncommitted changes" when the working tree has no real changes

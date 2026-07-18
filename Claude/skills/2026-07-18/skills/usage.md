# /usage

- Slug: `usage`
- Command: `/usage`
- Category: ops
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user asks about token or cost statistics

## Description

Show token usage and cost stats (merged /cost + /stats)

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Fixed `/usage` showing stale cached bars over fresher data, and `/mcp` not reclassifying
placeholder servers after config edits

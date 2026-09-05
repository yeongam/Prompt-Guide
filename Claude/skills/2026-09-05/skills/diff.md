# Diff Panel

- Slug: `diff`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.260` (CHANGELOG.md)
- Trigger: User wants to watch file changes live while Claude works, or review a session's diff so far.

## Procedure

1. Toggle `/diff` to open the panel beside the conversation.
2. Scroll the detail view with arrows, `j`/`k`, `PgUp`/`PgDn`, `Space`, `Home`/`End`.
3. Panel uses raw git blob content, ignoring workspace diff drivers/textconv (v2.1.222).

## Output

Live-updating uncommitted-changes diff view.

## Token Policy

- UI-only feature; no extra tokens consumed by toggling it.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content changed.

## Source Summary

> Added a diff panel that opens beside the conversation in fullscreen mode and shows your uncommitted changes as Claude edits; toggle it with `/diff`.

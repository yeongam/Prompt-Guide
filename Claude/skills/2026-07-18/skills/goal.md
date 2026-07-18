# /goal

- Slug: `goal`
- Command: `/goal`
- Category: ops
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.214`
- Trigger: user wants Claude to keep working across turns until a condition is met

## Description

Set a completion condition; shows live elapsed/turns/tokens overlay

## Token Policy

- One-line trigger and desc only; no duplicated upstream prose.
- Link to source repo/version instead of copying changelog text.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

Reduced idle CPU usage: `/goal` status chip no longer re-renders the terminal at 5 Hz
while idle, and fewer UI re-renders while subagents run in parallel

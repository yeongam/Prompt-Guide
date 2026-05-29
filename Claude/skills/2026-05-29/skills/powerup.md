# Power Up

- Slug: `powerup`
- Command: `/powerup`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants feature demos or to learn Claude Code features

## Description

Interactive animated feature demos with lessons

## Procedure

1. List available demos.
2. Play requested demo.
3. Show feature lesson.

## Output

Feature demo or lesson.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

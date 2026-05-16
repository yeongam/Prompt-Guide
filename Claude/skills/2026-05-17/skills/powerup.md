# Powerup

- Slug: `powerup`
- Command: `/powerup`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants feature demos or to learn Claude Code features

## Procedure

1. Launch interactive feature demo sequence.
2. Covers key Claude Code capabilities.

## Output

Interactive animated feature demos

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

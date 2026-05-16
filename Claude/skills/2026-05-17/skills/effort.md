# Effort

- Slug: `effort`
- Command: `/effort`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User wants to adjust effort/quality level

## Procedure

1. Display current effort level.
2. Accept new level (or read CLAUDE_EFFORT env var).
3. Apply to current session.

## Output

Updated session effort level

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

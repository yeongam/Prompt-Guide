# Effort

- Slug: `effort`
- Command: `/effort`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants to adjust effort/quality level

## Description

Interactive effort level slider for session

## Procedure

1. Display effort slider.
2. Apply selected level to session.

## Output

Effort level set confirmation.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

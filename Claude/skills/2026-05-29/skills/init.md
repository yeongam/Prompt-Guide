# Init

- Slug: `init`
- Command: `/init`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to initialize or document codebase

## Description

Generate CLAUDE.md with architecture, conventions, commands

## Procedure

1. Scan repo structure and conventions.
2. Extract key build/test/lint commands.
3. Write CLAUDE.md.

## Output

CLAUDE.md with architecture summary, commands, conventions.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

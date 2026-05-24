# Init

- Slug: `init`
- Cmd: `/init`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: initialize or document codebase

## Procedure

1. Scan repo structure and key files.
2. Extract conventions from existing code.
3. Write CLAUDE.md with commands, architecture, notes.

## Output

Generate CLAUDE.md with architecture, conventions, commands

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

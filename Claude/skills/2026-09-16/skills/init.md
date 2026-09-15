# Init

- Slug: `init`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: user asks to initialize or document a codebase

## Procedure

1. Scan repo structure, build tooling, and conventions.
2. Generate CLAUDE.md with architecture and commands.

## Output

CLAUDE.md documenting the codebase for future sessions.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

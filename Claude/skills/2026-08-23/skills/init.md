# Codebase Init

- Slug: `init`
- Category: documentation
- Source: https://github.com/anthropics/claude-code
- Source commit: `5cfc0a1905ce`
- Source version: 2.1.240
- Trigger: User asks to initialize or document an unfamiliar codebase.

## Procedure

1. Scan repo structure, build files, and existing docs.
2. Identify architecture, conventions, and common commands.
3. Write CLAUDE.md with concise, verifiable guidance.
4. Avoid restating what linters or type systems already enforce.

## Output

CLAUDE.md capturing architecture, conventions, and commands.

## Token Policy

- No repeated background context across turns.
- Return decision-critical output only.
- Reference the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

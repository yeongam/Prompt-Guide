# Init

- Slug: `init`
- Source: https://github.com/anthropics/claude-code
- Catalog version: `2.1.129`
- Trigger: user asks to initialize or document codebase

## Procedure

1. Scan project structure and detect language/framework.
2. Extract commands from package.json, Makefile, or README.
3. Write CLAUDE.md with architecture, conventions, and run commands.
4. Keep entries concise; link to source files.

## Output

CLAUDE.md file with codebase documentation.

## Token Policy

- Avoid duplicating info already in README.
- Link to source paths instead of copying content.
- One-line entries per convention.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

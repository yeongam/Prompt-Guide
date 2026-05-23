# Initialize Codebase

- Slug: `init`
- Command: `/init`
- Source: https://github.com/anthropics/claude-code
- Trigger: User asks to initialize or document codebase

## Procedure

1. Scan project structure, dependencies, entry points.
2. Identify frameworks, build tools, test commands.
3. Generate CLAUDE.md with architecture, conventions, commands.
4. Keep docs concise; omit obvious boilerplate.

## Output

CLAUDE.md with codebase architecture, conventions, key commands.

## Token Policy

- Generate only what fits in one screen.
- Link to existing docs instead of duplicating.
- Omit trivial details; focus on non-obvious conventions.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
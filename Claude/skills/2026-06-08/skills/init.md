# init

- Slug: `init`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to initialize or document codebase

## Procedure

Command: `/init`

Generate CLAUDE.md with codebase architecture, conventions, commands

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
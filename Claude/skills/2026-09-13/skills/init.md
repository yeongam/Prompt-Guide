# init

- Command: `/init`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.270`
- Trigger: user asks to initialize or document codebase

## Output

Generate CLAUDE.md with codebase architecture, conventions, commands

## Token Policy

- One canonical line per skill; no restated background context.
- Reference SKILLS_CATALOG.yaml instead of duplicating full docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

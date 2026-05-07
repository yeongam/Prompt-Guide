# Init (Codebase Docs)

- Slug   : `init`
- Source : https://github.com/anthropics/claude-code
- Version: 2.1.129
- Trigger: user asks to initialize or document codebase

## Procedure

1. Scan project tree and key config files.
2. Draft CLAUDE.md with architecture, conventions, commands.
3. Keep entries short; link to files instead of inlining.

## Output

CLAUDE.md covering project layout, stack, and run commands.

## Token Policy

- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

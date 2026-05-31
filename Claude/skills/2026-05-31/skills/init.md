# init

- Slug: `init`
- Cmd: `/init`
- Source: https://github.com/anthropics/claude-code
- Trigger: User asks to initialize or document codebase.

## Procedure

1. Scan repo structure, key files, and entry points.
2. Generate CLAUDE.md with architecture, conventions, and commands.
3. Keep sections concise; omit obvious details.

## Output

CLAUDE.md committed to repo root.

## Token Policy

- One-pass scan; skip binary/generated files.

## Compatibility

- Do not overwrite existing CLAUDE.md without diff check.

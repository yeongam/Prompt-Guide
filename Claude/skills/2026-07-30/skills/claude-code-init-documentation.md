# Codebase Init Documentation

- Slug: `claude-code-init-documentation`
- Command: `/init`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: User asks to initialize or document a codebase.

## Procedure

1. Scan repo structure, build system, and conventions.
2. Generate CLAUDE.md with architecture and commands.
3. Keep entries factual; avoid speculative guidance.

## Output

CLAUDE.md covering architecture, conventions, and commands.

## Token Policy

- Avoid repeated background context; use the catalog entry instead.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve SKILLS_CATALOG.yaml as the flat canonical reference.

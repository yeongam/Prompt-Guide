# Documentation Maintenance

- Slug: `documentation`
- Cmd: `/init`
- Source: https://github.com/anthropics/claude-code
- Source branch: `main`
- Catalog version: `2.1.161`
- Trigger: user asks to initialize or document codebase, generate CLAUDE.md

## Procedure

1. Scan repo structure, key files, and existing docs.
2. Generate CLAUDE.md covering architecture, conventions, commands.
3. Keep entries factual and concise.
4. Prefer existing naming conventions.
5. Verify completeness with grep for undocumented entry points.

## Output

CLAUDE.md with project overview, directory map, build/test commands, key conventions.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

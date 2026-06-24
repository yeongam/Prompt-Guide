# Documentation Maintenance

- Slug: `documentation-maintenance`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.187`
- Trigger: user asks to initialize, update, or generate CLAUDE.md or project documentation

## Procedure

1. Check official source alignment first.
2. Prefer smallest working documentation structure.
3. Keep architecture overview concise.
4. Document conventions and commands, not obvious patterns.
5. Verify docs reflect actual codebase state.

## Output

Concise documentation update with source traceability.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical documentation sections.
- Link to source files instead of duplicating content.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

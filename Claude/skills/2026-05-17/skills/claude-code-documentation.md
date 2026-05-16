# Claude Code Documentation

- Slug: `claude-code-documentation`
- Command: `(coding)`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User writes or updates CLAUDE.md, docs, or code comments

## Procedure

1. CLAUDE.md: architecture, build/test/lint commands, conventions.
2. Keep CLAUDE.md under 100 lines; link details elsewhere.
3. Code comments: only WHY, one line max.
4. No docstrings unless required by framework.
5. Prefer self-documenting names over comments.

## Output

Concise documentation following Claude Code conventions

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Init

- Slug: `init`
- Command: `/init`
- Category: skill
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User asks to initialize or document codebase

## Procedure

1. Scan project structure and key entry points.
2. Identify build/test/lint commands.
3. Summarize conventions and architecture.
4. Write concise CLAUDE.md under 100 lines.

## Output

CLAUDE.md with architecture, conventions, and commands

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

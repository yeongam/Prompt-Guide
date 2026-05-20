# Init Codebase

- Slug: `init`
- Cmd: `/init`
- Source: anthropics/claude-code v2.1.145
- Trigger: user asks to initialize or document codebase

## Procedure

1. Read existing code structure.
2. Extract conventions and commands.
3. Write concise CLAUDE.md.
4. Verify with /review.

## Output

CLAUDE.md documenting project structure and conventions.

## Token Policy

- Skip sections with no content.
- One sentence per convention.
- Link source files, don't inline them.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Init

- Slug: `init`
- Cmd: `/init`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to initialize or document the codebase

## Procedure

1. Scan repo structure, entry points, build scripts, and test commands.
2. Identify language/framework conventions.
3. Draft CLAUDE.md with: architecture overview, key commands, conventions, pitfalls.
4. Keep CLAUDE.md under 200 lines; link to deeper docs.
5. Commit result.

## Output

`CLAUDE.md` at repo root — compact architecture, commands, conventions.

## Token Policy

- CLAUDE.md is the deliverable; avoid verbose prose.
- Link to existing docs rather than duplicating them.
- One-sentence-per-section format.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

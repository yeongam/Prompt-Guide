# Init

- Slug: `init`
- Command: `/init`
- Category: docs
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Generate a CLAUDE.md capturing codebase architecture and conventions.

## Procedure

1. Scan repo structure, build tooling, and existing docs.
2. Extract commands, conventions, and architecture notes.
3. Write a single CLAUDE.md at the repo root.

## Output

New or refreshed CLAUDE.md file.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.

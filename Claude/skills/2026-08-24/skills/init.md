# Init

- Slug: `init`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: user asks to initialize or document a codebase

## Procedure

1. Scan the repo for architecture, conventions, and commands.
2. Generate a CLAUDE.md capturing what a new contributor needs.

## Output

CLAUDE.md with codebase architecture, conventions, and commands.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

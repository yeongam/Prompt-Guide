# Init

- Slug: `init`
- Category: documentation
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.223`
- Command: `/init`
- Trigger: user asks to initialize or document a codebase

## Output

Generates CLAUDE.md with architecture, conventions, and commands.

## Token Policy

- One-line trigger and output; no upstream docs copied.
- Reference CHANGELOG version instead of restating history.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Do not modify GPT or Gemini directories.

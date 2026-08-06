# Simplify

- Slug: `simplify`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.223`
- Command: `/simplify`
- Trigger: user asks to clean up or refactor changed code

## Output

Reviews changed code for reuse/quality/efficiency, then fixes issues.

## Token Policy

- One-line trigger and output; no upstream docs copied.
- Reference CHANGELOG version instead of restating history.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Do not modify GPT or Gemini directories.

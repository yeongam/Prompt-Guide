# Security Review

- Slug: `security-review`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.223`
- Command: `/security-review`
- Trigger: user asks for a security audit of pending changes

## Output

OWASP-focused audit of pending diffs; risk-ranked findings.

## Token Policy

- One-line trigger and output; no upstream docs copied.
- Reference CHANGELOG version instead of restating history.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Do not modify GPT or Gemini directories.

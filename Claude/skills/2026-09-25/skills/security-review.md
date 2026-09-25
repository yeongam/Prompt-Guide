# security-review

- Cmd: `/security-review`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: user asks security audit of current branch changes

## Desc

OWASP-focused audit of pending diffs; outputs risk-ranked findings

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

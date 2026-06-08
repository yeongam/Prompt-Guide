# security-review

- Slug: `security-review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks security audit of current branch changes

## Procedure

Command: `/security-review`

OWASP-focused audit of pending diffs; outputs risk-ranked findings

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
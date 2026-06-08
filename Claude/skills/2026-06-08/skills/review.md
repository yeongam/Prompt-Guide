# review

- Slug: `review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to review PR or branch

## Procedure

Command: `/review`

Multi-pass PR review; checks logic, style, security, tests

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
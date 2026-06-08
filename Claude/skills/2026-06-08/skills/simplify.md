# simplify

- Slug: `simplify`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to clean up or refactor changed code

## Procedure

Command: `/simplify`

Review changed code for reuse/quality/efficiency, then fix issues

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
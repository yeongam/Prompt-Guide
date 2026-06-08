# ultrareview

- Slug: `ultrareview`
- Source: https://github.com/anthropics/claude-code
- Trigger: user says "ultrareview" or wants multi-agent review

## Procedure

Command: `/ultrareview [PR#]`

Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
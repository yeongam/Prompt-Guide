# focus

- Slug: `focus`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants compact view of conversation

## Procedure

Command: `/focus`

Toggle focus view showing only: prompt + tool summary + final response

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
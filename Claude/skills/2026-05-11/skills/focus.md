# focus

- Cmd: `/focus`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants compact view of conversation

## Description

Toggle focus view showing only: prompt + tool summary + final response

## Token Policy

- Return only decision-critical output.
- Skip background context unless requested.
- Link to source instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.

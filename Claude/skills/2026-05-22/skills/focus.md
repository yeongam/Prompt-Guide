# focus

- Cmd: `/focus`
- Source: https://github.com/anthropics/claude-code
- Source commit: `1573399b48ff`
- Trigger: user wants compact view of conversation

## Description

Toggle focus view showing only: prompt + tool summary + final response

## Token Policy

- Reduces rendered context; lowers effective token overhead.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

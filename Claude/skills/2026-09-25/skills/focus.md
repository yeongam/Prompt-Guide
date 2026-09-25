# focus

- Cmd: `/focus`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: user wants a compact view of the conversation

## Desc

Toggle focus view showing only: prompt + tool summary + final response

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

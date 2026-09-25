# run

- Cmd: `/run`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: user asks to run, start, or screenshot the app to verify a change

## Desc

Launch and drive the project app; falls back to built-in patterns per project type

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

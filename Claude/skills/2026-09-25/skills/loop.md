# loop

- Cmd: `/loop [interval] [/command]`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: user wants a recurring task (e.g. "check every 5m", "keep running X")

## Desc

Run a prompt or slash command on a recurring interval (self-paced if no interval)

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

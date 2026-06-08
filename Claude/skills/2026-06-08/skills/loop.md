# loop

- Slug: `loop`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants recurring task (e.g. "check every 5m", "keep running X")

## Procedure

Command: `/loop [interval] [/command]`

Run prompt or slash command on recurring interval (default 10m)

## Token Policy

- Return only decision-critical instructions.
- Avoid repeated background context.
- Link to upstream repo instead of copying docs.

## Compatibility

- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or content changed.
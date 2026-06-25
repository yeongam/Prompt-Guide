# loop

**cmd:** `/loop [interval] [/command]`
**trigger:** user wants recurring task (e.g. "check every 5m", "keep running X")
**desc:** Run prompt or slash command on recurring interval (default 10m)
**example:** `"/loop 5m /review"`

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.
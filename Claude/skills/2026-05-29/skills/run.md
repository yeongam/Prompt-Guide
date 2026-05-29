# Run

- Slug: `run`
- Command: `/run`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to run, start, or screenshot the app

## Description

Launch project app and confirm changes work

## Procedure

1. Find project launch skill if available.
2. Detect project type: CLI/server/TUI/Electron/browser.
3. Launch and verify output.

## Output

Running app confirmation or screenshot.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

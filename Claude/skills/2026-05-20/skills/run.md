# Run App

- Slug: `run`
- Cmd: `/run`
- Source: anthropics/claude-code v2.1.145
- Trigger: user asks to run, start, or screenshot the app

## Procedure

1. Detect project type (CLI/server/TUI/browser).
2. Find launch command.
3. Start app.
4. Report ready state or errors.

## Output

App running confirmation with startup log snippet.

## Token Policy

- Show startup log tail only.
- Skip healthy check output.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

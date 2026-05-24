# Run

- Slug: `run`
- Cmd: `/run`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: run app, start server, launch project, screenshot app

## Procedure

1. Detect project type (server, CLI, TUI, Electron, browser).
2. Launch with appropriate command.
3. Verify golden path and report result.

## Output

Launch and drive project app to verify changes

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

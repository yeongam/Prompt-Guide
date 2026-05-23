# Run App

- Slug: `run`
- Command: `/run`
- Source: https://github.com/anthropics/claude-code
- Trigger: User asks to run, start, or screenshot the app; confirm a change works

## Procedure

1. Check for project-specific run skill first.
2. Detect project type: CLI, server, TUI, Electron, browser-driven, library.
3. Launch app with appropriate command.
4. Test golden path and edge cases; report regressions.

## Output

App running with confirmation of feature behavior.

## Token Policy

- Report only observed behavior delta, not full startup logs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
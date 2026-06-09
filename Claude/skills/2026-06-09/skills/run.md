# Run

- Slug: `run`
- Source: anthropics/claude-code (built-in skill)
- Trigger: User wants to launch and observe the app, confirm a change works in the real app, or screenshot the UI.

## Procedure

1. Check for a project-specific skill covering app launch first.
2. Detect project type (CLI, server, TUI, Electron, browser-driven, library).
3. Start the app using the appropriate launch command.
4. Test the golden path and key edge cases.
5. Monitor for regressions in adjacent features.
6. Report observed behavior; note any failures.

## Output

Observed runtime behavior with pass/fail per tested scenario.

## Token Policy

- Report only deviations from expected behavior.
- No full build log unless an error occurred.

## Compatibility

- Available in all Claude Code environments.
- Type checking and tests verify code correctness; this skill verifies feature correctness.

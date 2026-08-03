# App Launch and Verification

- Slug: `run`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: Asked to run/start/screenshot the app, or to confirm a change works in the real app (not just via tests).

## Procedure

1. Look for a project-specific launch skill/script first.
2. Fall back to built-in patterns by project type (CLI, server, TUI, Electron, browser-driven, library).
3. Exercise the golden path and relevant edge cases, not just a bare launch.
4. Watch for regressions in adjacent features while verifying.

## Output

Confirmed working behavior in the actual running app (screenshot/log evidence where applicable).

## Token Policy

- Capture only the relevant log/screenshot slice, not full verbose output.

## Compatibility

- Additive only; no collision with existing catalog entries.

# Session Start Hook

- Slug: `session-start-hook`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: user sets up a repo for Claude Code on the web and wants tests/linters to run automatically

## Procedure

1. Create a SessionStart hook that prepares the environment.
2. Ensure the project can run its tests and linters during web sessions.

## Output

Configured SessionStart hook for Claude Code on the web.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

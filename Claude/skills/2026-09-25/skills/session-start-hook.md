# session-start-hook

- Cmd: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Desc

Create SessionStart hook ensuring project can run tests and linters

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

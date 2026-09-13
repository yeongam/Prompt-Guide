# session-start-hook

- Command: `/session-start-hook`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.270`
- Trigger: user wants test/lint runners on session start (web Claude Code)

## Output

Create SessionStart hook ensuring project can run tests and linters

## Token Policy

- One canonical line per skill; no restated background context.
- Reference SKILLS_CATALOG.yaml instead of duplicating full docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

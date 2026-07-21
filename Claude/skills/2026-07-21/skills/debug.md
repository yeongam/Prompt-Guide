# Debug

- Slug: `debug`
- Command: `/debug`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.216`
- Trigger: user asks Claude to help troubleshoot the current session

## Procedure

1. Toggle debug logging on for the session.
2. Reproduce the issue and capture relevant logs.
3. Summarize the likely cause with log evidence.

## Output

Debug logging enabled plus a session-issue diagnosis.

## Token Policy

- Avoid repeated background context; return only decision-critical output.
- Link to the official repo instead of copying changelog prose.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate into Claude/skills/SKILLS_CATALOG.yaml only if slug is new or hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Debug logs are no longer written by default; /debug toggles them on mid-session.

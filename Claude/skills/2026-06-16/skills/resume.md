# /resume — Resume Background Session

- Slug: `resume`
- Cmd: `/resume [session-id]`
- Added: v2.1.144
- Trigger: User wants to return to a background session or view its output.

## Procedure

1. `/resume` without args: list all resumable sessions.
2. `/resume <id>`: attach to specific background session.
3. Background sessions started with `claude --bg --exec` are resumable.

## Output

Attached session with full context restored.

## Token Policy

- Show session list compactly (id, status, last activity).
- No repeated context on resume.

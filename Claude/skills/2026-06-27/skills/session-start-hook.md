# /session-start-hook — session-start-hook

- Category : `config`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user wants test/lint runners on session start.

**Action** : Create SessionStart hook for test/lint runners (web Claude Code).

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

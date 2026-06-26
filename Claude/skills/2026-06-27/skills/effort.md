# /effort — effort

- Category : `config`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user wants to adjust effort/quality level.

**Action** : Interactive slider for session effort level (also: CLAUDE_EFFORT env var).

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

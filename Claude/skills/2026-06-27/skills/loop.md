# /loop [interval] [cmd] — loop

- Category : `automation`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user wants recurring task ("check every 5m", "keep running X").

**Action** : Run prompt/slash command on recurring interval (default 10m).

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

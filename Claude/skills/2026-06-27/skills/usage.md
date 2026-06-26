# /usage — usage

- Category : `ux`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user asks about token or cost statistics.

**Action** : Show token usage and cost stats (merged /cost + /stats).

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

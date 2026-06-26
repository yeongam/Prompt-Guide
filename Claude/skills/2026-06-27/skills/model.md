# /model — model

- Category : `config`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user wants to switch the active model.

**Action** : Select or display the current Claude model (opus/sonnet/haiku).

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

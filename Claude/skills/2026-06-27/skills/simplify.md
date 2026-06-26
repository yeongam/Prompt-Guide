# /simplify — simplify

- Category : `core`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user asks to clean up or refactor changed code.

**Action** : Review changed code for reuse/quality/efficiency then fix.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

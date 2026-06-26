# /verify — verify

- Category : `dev`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user asks to verify a PR or confirm a fix works.

**Action** : Run app and observe behavior to confirm change is correct.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

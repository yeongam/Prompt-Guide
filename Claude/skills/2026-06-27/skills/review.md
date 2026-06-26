# /review — review

- Category : `core`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user asks to review PR or branch.

**Action** : Multi-pass PR review: logic, style, security, tests.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

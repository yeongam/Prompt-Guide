# /security-review — security-review

- Category : `core`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user asks security audit of current branch.

**Action** : OWASP-focused audit of pending diffs; risk-ranked findings.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

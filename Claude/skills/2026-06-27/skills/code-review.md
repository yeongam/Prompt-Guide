# /code-review — code-review

- Category : `core`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user asks for code review on current diff.

**Action** : Review diff for correctness, reuse, efficiency; optional PR comments/fix.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

# /deep-research — deep-research

- Category : `research`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user wants multi-source fact-checked research report.

**Action** : Fan-out web searches, fetch sources, adversarial verify, cited report.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

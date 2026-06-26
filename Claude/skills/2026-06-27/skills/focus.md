# /focus — focus

- Category : `ux`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user wants compact view of conversation.

**Action** : Toggle focus view: prompt + tool summary + final response only.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

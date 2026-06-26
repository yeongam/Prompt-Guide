# /update-config — update-config

- Category : `config`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: automated behavior requests ("when X", "allow Y", "set Z=val").

**Action** : Configure settings.json: hooks, permissions, env vars.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

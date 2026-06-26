# /init — init

- Category : `core`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user asks to initialize or document codebase.

**Action** : Generate CLAUDE.md with architecture, conventions, commands.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

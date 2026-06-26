# /ultraplan — ultraplan

- Category : `advanced`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user wants cloud environment for complex planning.

**Action** : Auto-create cloud worktrees for multi-agent planning tasks.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

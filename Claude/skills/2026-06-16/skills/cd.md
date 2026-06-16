# /cd — Change Working Directory

- Slug: `cd`
- Cmd: `/cd <path>`
- Added: v2.1.169
- Trigger: User wants to switch working directory mid-session without breaking prompt cache.

## Procedure

1. Run `/cd <path>` to move session to new directory.
2. Prompt cache is preserved; MCP servers are not restarted.
3. CLAUDE.md, plugins, and skills reload from new directory context.

## Output

Session working directory updated; no cache invalidation.

## Token Policy

- No repeated context; one-line confirmation only.
- Link to docs instead of explaining path resolution rules.

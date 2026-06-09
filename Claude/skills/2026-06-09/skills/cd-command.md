# CD Command

- Slug: `cd-command`
- Source: anthropics/claude-code v2.1.169
- Trigger: User wants to change working directory without breaking prompt cache.

## Procedure

1. Use `/cd <path>` to move session to new directory.
2. Prompt cache is preserved; session context remains intact.
3. Useful for multi-root monorepos or switching between sub-projects mid-session.

## Output

Confirmation of new working directory. No context loss.

## Token Policy

- No repeated context after directory change.
- Return only the new path confirmation.

## Compatibility

- Added: v2.1.169
- No conflict with existing skills.

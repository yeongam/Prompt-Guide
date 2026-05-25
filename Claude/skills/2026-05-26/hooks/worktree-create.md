# Worktree Create

- Slug: `worktree-create`
- Event: `WorktreeCreate`
- Source: https://github.com/anthropics/claude-code
- Source commit: `offline`
- Trigger: Custom worktree provisioning via HTTP endpoint.

## Checks

1. Verify worktree path is available.
2. Confirm branch name is valid.

## Actions

- Return hookSpecificOutput.worktreePath for custom path.
- Provision worktree-specific resources (containers, secrets).

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Fires on worktree creation; supports HTTP endpoint (added v2.1.88)

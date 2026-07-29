# Worktree Create Provisioner

- Slug: `worktree-create-provisioner`
- Event: `WorktreeCreate`
- Source: https://github.com/anthropics/claude-code (v2.1.220)
- Trigger: Fires on worktree creation (added v2.1.88).

## Checks

1. Verify the HTTP endpoint returns a valid worktreePath.

## Actions

- Provision the worktree via the configured HTTP endpoint.

## Token Policy

- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.

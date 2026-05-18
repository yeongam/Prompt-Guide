# Agent Workflow Guard

- Slug: `agent-workflow-guard`
- Event: `post_apply`
- Source: https://github.com/openai/openai-agents-python
- Source commit: `65774ce88d98`
- Trigger: Run after applying agent workflow guidance.

## Checks

1. Confirm tools, handoffs, and orchestration guidance stay separated.
2. Prefer minimal runnable workflow patterns.
3. Preserve existing GPT skill behavior when adding agent guidance.

## Actions

- Record agent workflow conflicts in the changelog.
- Keep agent guidance short enough for fast reuse.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify Claude or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Framework for multi-agent workflows

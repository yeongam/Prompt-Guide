# Agent SDK Workflow Guard

- Slug: `agent-sdk-workflow-guard`
- Event: `post_apply`
- Source: https://github.com/anthropics/claude-agent-sdk-python
- Source commit: `57f67cd12cdb`
- Trigger: Run after applying Agent SDK workflow guidance.

## Checks

1. Confirm tools, handoffs, and orchestration guidance stay separated.
2. Prefer minimal runnable workflow patterns.
3. Preserve existing Claude skill behavior when adding agent guidance.

## Actions

- Record agent workflow conflicts in the changelog.
- Keep agent guidance short enough for fast reuse.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or Gemini directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Build custom agents on top of Claude Code with the Agent SDK

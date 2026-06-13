# MCP Compatibility Check

- Slug: `mcp-compatibility-check`
- Event: `pre_apply`
- Source: https://github.com/anthropics/model-context-protocol
- Source commit: `bootstrap-2026-06-13`
- Trigger: Run before applying MCP server or tool guidance.

## Checks

1. Verify MCP spec version alignment with the source commit.
2. Confirm tool definitions use correct schema structure.
3. Keep server-side and client-side guidance clearly separated.

## Actions

- Attach spec commit to MCP skill output.
- Flag schema conflicts in the changelog conflict section.

## Token Policy

- Do not copy upstream documents into hook output.
- Keep hook cards short enough for quick pre/post-run loading.
- Prefer catalog metadata over repeated inline context.

## Compatibility

- Do not modify GPT or other provider directories.
- Do not overwrite existing dated hook snapshots.
- Record hook conflicts in the same dated changelog as skills.

## Source Summary

Model Context Protocol specification.

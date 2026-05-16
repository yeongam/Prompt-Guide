# Claude Code Subagent SDK

- Slug: `claude-code-subagent-sdk`
- Command: `(coding)`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User builds multi-agent workflows with Claude Agent SDK

## Procedure

1. Use Agent tool for tasks exceeding 3 search queries or needing isolation.
2. Pass self-contained prompts; agents have no prior context.
3. Specify subagent_type for specialized agents (Explore, Plan, etc.).
4. Run independent agents in parallel via single message multi-call.
5. Trust but verify: check agent output before reporting success.

## Output

Agent orchestration code with proper tool delegation

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

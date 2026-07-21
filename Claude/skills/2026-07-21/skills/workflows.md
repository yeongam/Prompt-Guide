# Workflows

- Slug: `workflows`
- Command: `/workflows`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.216`
- Trigger: user explicitly asks for multi-agent orchestration of a task

## Procedure

1. Confirm explicit user opt-in before spawning a fleet.
2. Script the phases: fan-out, verify, synthesize.
3. Track live runs and progress via /workflows.

## Output

A background multi-agent run orchestrating tens to hundreds of agents.

## Token Policy

- Avoid repeated background context; return only decision-critical output.
- Link to the official repo instead of copying changelog prose.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate into Claude/skills/SKILLS_CATALOG.yaml only if slug is new or hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

Dynamic workflows orchestrate work across many agents in the background for larger, more complex tasks; /workflows views current runs.

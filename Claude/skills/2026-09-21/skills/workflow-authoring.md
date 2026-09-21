# Workflow Authoring

- Command: `Workflow tool (script API)`
- Slug: `workflow-authoring`
- Source: https://github.com/anthropics/claude-code
- Since: `2.1.130`
- Trigger: user opts into multi-agent orchestration for a task

## Procedure

1. Load before writing a Workflow script: script API, resume, quality patterns.
2. Respect the session's workflow size guideline unless the user asks for a different scale.
3. Use pipeline()/parallel()/agent() to fan work out and verify findings as they land.

## Output

A workflow script ready to run via the Workflow tool.

## Token Policy

- One canonical card per skill; no duplicated background context.
- Procedure capped at three steps; link to source instead of copying docs.

## Compatibility

- Additive only: does not modify or remove existing flat-catalog entries.
- Does not touch GPT/ or Gemini/ directories.

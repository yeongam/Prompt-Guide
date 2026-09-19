# Workflow Authoring

- Slug: `workflow-authoring`
- Cmd: `/workflows`
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md, v2.1.278)
- Trigger: user explicitly opts into multi-agent orchestration (pipeline/parallel subagents).

## Procedure

1. Only load when the user opted in (keyword, session flag, or explicit ask).
2. Keep workflows under the configured size guideline unless told otherwise.
3. Prefer `pipeline`/`parallel` composition over ad hoc agent spawning.

## Token Policy

- Reference guide only; do not inline full worked examples here.

## Compatibility

- Do not modify GPT or Gemini directories.
- New entry; no conflict with existing catalog slugs.

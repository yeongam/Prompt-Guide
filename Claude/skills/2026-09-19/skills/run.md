# Run

- Slug: `run`
- Cmd: `/run` (skill, launches/drives the app)
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md, v2.1.278)
- Trigger: user asks to run, start, or screenshot the app, or confirm a change works live.

## Procedure

1. Look for a project-specific launch skill first.
2. Otherwise fall back to built-in patterns by project type (CLI, server, TUI, Electron, browser, library).

## Token Policy

- Report only; do not duplicate project run instructions here.

## Compatibility

- Do not modify GPT or Gemini directories.
- New entry; no conflict with existing catalog slugs.

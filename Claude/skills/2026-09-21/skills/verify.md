# Verify

- Command: `/verify`
- Slug: `verify`
- Source: https://github.com/anthropics/claude-code
- Since: `2.1.215`
- Trigger: user wants pending changes checked before finishing a task

## Procedure

1. Run the project's fast checks (lint, typecheck, unit tests) on the diff.
2. Re-read the diff adversarially for correctness issues.
3. Report pass/fail per check; do not auto-fix silently.

## Output

Pass/fail checklist for the current change set.

## Token Policy

- One canonical card per skill; no duplicated background context.
- Procedure capped at three steps; link to source instead of copying docs.

## Compatibility

- Additive only: does not modify or remove existing flat-catalog entries.
- Does not touch GPT/ or Gemini/ directories.

# Plugin Eval

- Command: `claude plugin eval`
- Slug: `plugin-eval`
- Source: https://github.com/anthropics/claude-code
- Since: `2.1.269`
- Trigger: user wants to test or score a plugin's eval suite

## Procedure

1. Run a plugin's eval suite against Claude Code.
2. Produce scored, reproducible results.
3. Emit both JSON and HTML report formats.

## Output

JSON + HTML eval report for the plugin under test.

## Token Policy

- One canonical card per skill; no duplicated background context.
- Procedure capped at three steps; link to source instead of copying docs.

## Compatibility

- Additive only: does not modify or remove existing flat-catalog entries.
- Does not touch GPT/ or Gemini/ directories.

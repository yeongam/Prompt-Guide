# Claude API

- Slug: `claude-api`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: Code imports the `anthropic` SDK, or the user asks about Claude API / Anthropic SDK features (pricing, model choice, caching, streaming, tool use, MCP, model migration).

## Procedure

1. Check whether the project targets the Python or TypeScript/JS `anthropic` SDK.
2. For migration work, use the `upgrade` subcommand to move Python projects from SDK 0.x to 1.x (`anthropic.Timeout` replaces old timeout handling).
3. For prompt/tool auditing, use the `prompt-audit` subcommand.
4. Reference current model ids and pricing rather than memorized defaults.
5. Verify with the narrowest relevant Anthropic API doc section.

## Output

Working Claude API integration code, or a migration/audit report, grounded in current SDK/model reality.

## Token Policy

- Reuse the canonical entry in `Claude/skills/SKILLS_CATALOG.yaml`; do not restate the full model table here.
- Link to source doc sections instead of copying long API reference text.

## Compatibility

- Do not overwrite existing dated skill snapshots; integrate only if content changed.
- Reference model ids from this catalog's `models:` block, not the model's own training-time knowledge (which predates later releases).

## Source Summary

Official Claude Code skill for building/debugging Claude API apps. `upgrade` subcommand (Python 0.x→1.x SDK migration) added v2.1.239; `prompt-audit` subcommand added v2.1.221. Default reference model bumped to Claude Opus 5 as of v2.1.219.

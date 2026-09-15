# Claude API

- Slug: `claude-api`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: code imports the anthropic SDK, or user asks about Claude API features

## Procedure

1. Context cost cut from ~200k+ to ~25k tokens via on-demand reference docs.
2. `upgrade` subcommand migrates Python projects from anthropic 0.x to 1.x.
3. `prompt-audit` subcommand audits prompts/tool descriptions for stale patterns.
4. Covers Admin API (members, invites, workspaces, keys, rate limits, CMEK).

## Output

API/SDK guidance, migration steps, or a prompt audit report.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

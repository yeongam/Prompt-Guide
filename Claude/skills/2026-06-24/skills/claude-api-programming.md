# Claude API Programming

- Slug: `claude-api-programming`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.187`
- Trigger: code imports anthropic SDK; user asks about Claude API, tool use, streaming, caching

## Procedure

1. Check official source alignment first.
2. Prefer smallest working implementation.
3. Use structured tool-use APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Compact API implementation checklist with model/pricing alignment.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

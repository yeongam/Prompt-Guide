# Claude Code API Integration

- Slug: `claude-code-api-integration`
- Command: `(coding)`
- Category: coding
- Source: https://github.com/anthropics/claude-code
- Source commit: `local`
- Version: 2.1.129
- Trigger: User implements Claude API; needs caching, tool use, or model migration

## Procedure

1. Import anthropic SDK; AsyncAnthropic for async paths.
2. Add cache_control={'type':'ephemeral'} on system/large context blocks.
3. Use current IDs: claude-opus-4-7, claude-sonnet-4-6, claude-haiku-4-5-20251001.
4. Define tools with minimal JSON schema.
5. Handle tool_use blocks in response loop.

## Output

Optimized API code with correct model IDs and caching

## Token Policy

- Return only decision-critical content.
- Link to source repo instead of copying long docs.
- Avoid repeated background context across turns.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Anthropic Python SDK

- Slug: `anthropic-python-sdk`
- Source: https://github.com/anthropics/anthropic-sdk-python
- Source commit: `unknown`
- Trigger: Use for implementing Claude API features in Python: streaming, tool use, prompt caching.

## Procedure

1. Import anthropic and instantiate client with ANTHROPIC_API_KEY.
2. Use messages.create for standard calls; messages.stream for streaming.
3. Add cache_control to system prompt and large context blocks for caching.
4. Define tools with name, description, and input_schema (JSON Schema).
5. Model IDs: claude-sonnet-4-6, claude-opus-4-7, claude-haiku-4-5.

## Output

Minimal Python snippet aligned with current SDK version.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

# Claude SDK for Python [![PyPI version](https://img.shields.io/pypi/v/anthropic.svg)](h
ttps://pypi.org/project/anthropic/) The Claude SDK for Python provides access to the
[Claude API](https://docs.anthropic.com/en/api/) from Python applications. ##
Documentation Full documentation is available at **[platform.claude.com/docs/en/api/sdks
/python](https://platform.claude.com/docs/en/api/sdks/python)**. ## Installation.

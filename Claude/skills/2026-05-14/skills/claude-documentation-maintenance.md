# Claude Documentation Maintenance

- Slug: `claude-documentation-maintenance`
- Source: https://github.com/anthropics/anthropic-sdk-python
- Source commit: `unknown`
- Trigger: Use for updating docs, examples, prompts, and guides for Claude integrations.

## Procedure

1. Check official Anthropic source alignment first.
2. Prefer smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Concise documentation checklist with Anthropic source traceability.

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

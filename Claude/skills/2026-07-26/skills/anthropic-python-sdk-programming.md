# Anthropic Python SDK Programming

- Slug: `anthropic-python-sdk-programming`
- Source: https://github.com/anthropics/anthropic-sdk-python
- Source ref: `README.md` (branch `main`)
- CLI version context: 2.1.220
- Trigger: Use for direct Messages API calls, streaming, and tool-use loops in Python.

## Procedure

1. Check the official source file for current behavior before answering.
2. Prefer the smallest working implementation.
3. Use structured APIs/config keys over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command or test.

## Output

Lean Messages API implementation checklist.

## Token Policy

- Avoid repeated background context across turns.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Do not modify GPT or Gemini directories.
- Preserve changelog evidence for every generated update.

## Source Summary

# Claude SDK for Python [![PyPI version](https://img.shields.io/pypi/v/anthropic.svg)](h
ttps://pypi.org/project/anthropic/) The Claude SDK for Python provides access to the
[Claude API](https://docs.anthropic.com/en/api/) from Python applications. ##
Documentation Full documentation is available at **[platform.claude.com/docs/en/api/sdks
/python](https://platform.claude.com/docs/en/api/sdks/python)**. ## Installation.

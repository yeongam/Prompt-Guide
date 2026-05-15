# Python SDK Programming

- Slug: `python-sdk-programming`
- Source: https://github.com/openai/openai-python
- Source commit: `38d75d74a562`
- Trigger: Use for Python SDK integration, request structure, and migration checks.

## Procedure

1. Check official source alignment first.
2. Prefer smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Minimal Python SDK guidance with verification steps.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

# OpenAI Python API library [![PyPI version](https://img.shields.io/pypi/v/openai.svg?la
bel=pypi%20(stable))](https://pypi.org/project/openai/) The OpenAI Python library
provides convenient access to the OpenAI REST API from any Python 3.9+ application. The
library includes type definitions for all request params and response fields, and offers
both synchronous and asynchronous clients powered by [httpx](https://git.

# Agents Workflow Programming

- Slug: `agents-workflow-programming`
- Source: https://github.com/openai/openai-agents-python
- Source commit: `9514473c234c`
- Trigger: Use for agent workflows, handoffs, tools, and orchestration code.

## Procedure

1. Check official source alignment first.
2. Prefer smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Lean agent workflow design and implementation checks.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

# OpenAI Agents SDK [![PyPI](https://img.shields.io/pypi/v/openai-
agents?label=pypi%20package)](https://pypi.org/project/openai-agents/) The OpenAI Agents
SDK is a lightweight yet powerful framework for building multi-agent workflows. It is
provider-agnostic, supporting the OpenAI Responses and Chat Completions APIs, as well as
100+ other LLMs. > [!NOTE] > Looking for the JavaScript/TypeScript version? Check out
[Ag.

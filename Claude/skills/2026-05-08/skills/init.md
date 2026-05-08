# Init (Codebase Documentation)

- Slug: `init`
- Command: `/init`
- Trigger: user asks to initialize or document codebase
- Source: https://github.com/anthropics/claude-code

## Description

Generate CLAUDE.md with architecture, conventions, and commands

## Procedure

1. Scan repo structure, entry points, and config files.
2. Extract build/test/lint commands from package.json or Makefile.
3. Document key directories, naming conventions, and gotchas.
4. Keep CLAUDE.md under 200 lines; link to external docs.

## Output

CLAUDE.md ready for Claude Code to load as project context.

## Token Policy

- One-line descriptions; no multi-paragraph docstrings.
- Omit obvious stdlib/framework behavior.

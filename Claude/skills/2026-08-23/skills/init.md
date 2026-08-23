# Init

- Slug: `init`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: User asks to initialize or document a codebase.

## Procedure

1. Survey the codebase's architecture, conventions, and common commands (build/test/lint).
2. Generate or update `CLAUDE.md` with that context.

## Output

A `CLAUDE.md` file capturing project-specific guidance for future sessions.

## Token Policy

- Reuse the canonical entry in `Claude/skills/SKILLS_CATALOG.yaml` instead of duplicating it here.

## Compatibility

- Do not overwrite existing dated skill snapshots; integrate only if content changed.

## Source Summary

Official Claude Code skill: generates `CLAUDE.md` with codebase architecture, conventions, and commands. No changelog-visible behavior change between v2.1.129 and v2.1.241.

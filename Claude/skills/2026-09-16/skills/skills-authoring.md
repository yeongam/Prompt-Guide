# Skills Authoring & Maintenance

- Slug: `skills-authoring`
- Source: https://github.com/anthropics/skills
- Source ref: main (fetched 2026-09-16)
- Trigger: Use for creating, updating, or documenting Claude Skills (SKILL.md, structure, conventions).

## Procedure

1. Check the official source for the current API/CLI shape before coding.
2. Prefer the smallest working implementation over speculative abstractions.
3. Use the SDK's structured types/tools instead of hand-rolled parsing.
4. Keep generated snippets short; link back to the source repo for depth.
5. Verify with the narrowest relevant command or test before finishing.

## Output

Checklist for authoring or syncing skills consistent with Anthropic's official skills repo.

## Token Policy

- Avoid repeating background context already in the source repo.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs verbatim.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content changed.
- Preserve changelog evidence for every generated update.

## Source Summary

> **Note:** This repository contains Anthropic's implementation of skills for Claude. Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks — teaching Claude how to complete specific tasks in a repeatable way, whether that's creating.

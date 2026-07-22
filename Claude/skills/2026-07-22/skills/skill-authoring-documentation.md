# Skill Authoring Documentation

- Slug: `skill-authoring-documentation`
- Source: https://github.com/anthropics/skills
- Source ref (content fingerprint): `2fb9c4cc0263`
- Trigger: Use for creating, updating, or documenting Claude Code skills.

## Procedure

1. Check official source alignment first.
2. Prefer smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Concise skill-authoring checklist with source traceability.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

## Source Summary

> **Note:** This repository contains Anthropic's implementation of skills for Claude.
For information about the Agent Skills standard, see
[agentskills.io](http://agentskills.io). [![skills.sh](https://skills.sh/b/anthropics/sk
ills)](https://skills.sh/anthropics/skills) # Skills Skills are folders of instructions,
scripts, and resources that Claude loads dynamically to improve performance on
specialized tasks. Skill.

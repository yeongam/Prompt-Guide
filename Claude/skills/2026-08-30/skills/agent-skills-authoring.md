# Agent Skills Authoring

- Slug: `agent-skills-authoring`
- Source: https://github.com/anthropics/skills
- Source ref: `2fb9c4cc0263`
- Trigger: Use for creating, editing, or applying SKILL.md-based skills, incl. docx/pdf/pptx/xlsx.

## Procedure

1. Check official source alignment first.
2. Prefer the smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Minimal skill-authoring checklist with SKILL.md frontmatter rules.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to the source repo instead of copying long docs.

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

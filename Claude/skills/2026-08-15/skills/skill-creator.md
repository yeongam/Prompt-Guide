# skill-creator

- Slug: `skill-creator`
- Source: https://github.com/anthropics/skills/tree/main/skills/skill-creator
- Source commit: `ref:main`
- Trigger: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with vari.

## Output

Compact, repeatable instructions for the task the skill covers.

## Token Policy

- Reference the upstream SKILL.md instead of copying its full body.
- Keep the local card to trigger + one-line output + policy notes.
- Load full skill content only when the skill actually fires.

## Compatibility

- Namespaced separately from Claude Code slash-command skills.
- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

# Skill Creator A skill for creating new skills and iteratively improving them. At a high level, the process of creating a skill goes like this: - Decide what you want the skill to do and roughly how it should do it - Write a draft of the skill - Create a few test prompts and run claude-with-access-to-the-skill on them - Help the user evaluate the results both qualitatively and quantitatively - While the runs happen.

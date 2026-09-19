# Skill Doctor

- Slug: `skill-doctor`
- Cmd: `/skill-doctor`
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md, v2.1.278)
- Trigger: user wants to prune unused or context-expensive loaded skills.

## Procedure

1. List loaded skills with their context cost.
2. Flag skills unused this session.
3. Suggest which to disable via skillOverrides.

## Token Policy

- Report only; do not duplicate skill bodies here.

## Compatibility

- Do not modify GPT or Gemini directories.
- New entry; no conflict with existing catalog slugs.

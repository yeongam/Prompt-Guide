# Reload Skills

- Slug: `reload-skills`
- Cmd: `/reload-skills`
- Source: https://github.com/anthropics/claude-code (CHANGELOG.md, v2.1.278)
- Trigger: user edited/added a skill file and wants it picked up without restarting.

## Procedure

1. Re-scan configured skill directories.
2. Refresh the slash-command menu to match.

## Token Policy

- Report only; no skill body duplication.

## Compatibility

- Do not modify GPT or Gemini directories.
- New entry; no conflict with existing catalog slugs.

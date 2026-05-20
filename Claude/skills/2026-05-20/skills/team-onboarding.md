# Team Onboarding

- Slug: `team-onboarding`
- Cmd: `/team-onboarding`
- Source: anthropics/claude-code v2.1.145
- Trigger: user wants teammate ramp-up guide

## Procedure

1. Read CLAUDE.md and usage history.
2. Identify common tasks.
3. Write step-by-step guide.
4. Include key commands.

## Output

Onboarding guide markdown with project-specific tips.

## Token Policy

- One sentence per tip.
- Skip generic advice already in README.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

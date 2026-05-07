# Team Onboarding (Docs)

- Slug   : `team-onboarding`
- Source : https://github.com/anthropics/claude-code
- Version: 2.1.129
- Trigger: user wants teammate ramp-up guide from project history

## Procedure

1. Mine local Claude Code usage history.
2. Draft guide: setup, conventions, key commands.
3. Keep under 500 tokens.

## Output

Concise teammate onboarding guide.

## Token Policy

- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

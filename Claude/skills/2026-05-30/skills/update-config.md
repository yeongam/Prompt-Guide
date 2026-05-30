# Update Config

- Slug: `update-config`
- Cmd: `/update-config`
- Source: https://github.com/anthropics/claude-code
- Trigger: automated behavior ("from now on when X", "allow Y", "set Z=val", "whenever X", "before/after X")

## Scope

| Intent | Action |
|--------|--------|
| Automated behavior | Add hook to `hooks` array |
| Permission allow | Add to `allowedTools` |
| Env var | Add to `env` block |
| Model setting | Update `model` field |

## Files

- Project: `.claude/settings.json`
- User: `~/.claude/settings.json`

## Procedure

1. Identify intent type (hook / permission / env / model).
2. Read current settings file.
3. Merge change minimally.
4. Write updated settings.
5. Confirm scope (project vs user).

## Token Policy

- Return JSON diff/patch only.
- Note scope (project/user) in one line.
- No verbose explanation of hook schema.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

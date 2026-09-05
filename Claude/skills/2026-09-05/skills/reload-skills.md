# Reload Skills

- Slug: `reload-skills`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.152` (CHANGELOG.md)
- Trigger: A skill file changed on disk (e.g. this daily sync) and needs picking up mid-session.

## Procedure

1. Run `/reload-skills` after editing or adding skill files.
2. Or have a `SessionStart` hook return `{reloadSkills: true}` to do it automatically.

## Output

Session picks up new/changed skills without a restart.

## Token Policy

- Cheaper than restarting the session; conversation cache is preserved.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content changed.

## Source Summary

> Added `/reload-skills` command to re-scan skill directories without restarting the session. `SessionStart` hooks can now return `reloadSkills: true` to re-scan skill directories, making skills installed by the hook available in the same session.

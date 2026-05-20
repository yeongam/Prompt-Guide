# Update Config

- Slug: `update-config`
- Cmd: `/update-config`
- Source: anthropics/claude-code v2.1.145
- Trigger: automated behavior requests (when X, allow Y, set Z=val)

## Procedure

1. Identify target config scope (project/user).
2. Locate or create settings.json.
3. Apply minimal change.
4. Confirm effect.

## Output

Updated settings.json diff.

## Token Policy

- Emit only changed JSON keys.
- No full-file reprint.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

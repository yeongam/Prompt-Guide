# Verify

- Slug: `verify`
- Cmd: `/verify`
- Source: https://github.com/anthropics/claude-code
- Version: 2.1.150
- Trigger: verify fix works, confirm feature works, validate before push

## Procedure

1. Identify what the change is supposed to do.
2. Launch app and exercise the changed path.
3. Report pass/fail with evidence.

## Output

Run app and observe behavior to confirm a code change

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Verify Change

- Slug: `verify`
- Cmd: `/verify`
- Source: anthropics/claude-code v2.1.145
- Trigger: user asks to verify a change works, confirm a fix, or test manually

## Procedure

1. Identify golden path to test.
2. Run app or relevant command.
3. Observe output against expectation.
4. Report edge case regressions if found.

## Output

Pass/fail result with observed behavior summary.

## Token Policy

- Report result + one-line evidence only.
- Skip steps that succeeded without incident.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

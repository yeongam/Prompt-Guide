# Run

- Slug: `run`
- Source: https://github.com/anthropics/claude-code @ `v2.1.272`
- Trigger: user asks to run, start, or screenshot the app to confirm a change works

## Procedure

1. Prefer a project skill that already covers launching the app.
2. Otherwise fall back to built-in patterns per project type.

## Output

The app running with the change verified live, not just by tests.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical instructions.
- Link to the official repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

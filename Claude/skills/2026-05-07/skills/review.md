# Review (PR/Branch)

- Slug   : `review`
- Source : https://github.com/anthropics/claude-code
- Version: 2.1.129
- Trigger: user asks to review PR or branch changes

## Procedure

1. Check logic correctness.
2. Flag style and naming deviations.
3. Identify security and test gaps.
4. Return ranked findings only.

## Output

Risk-ranked review with actionable fix suggestions.

## Token Policy

- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

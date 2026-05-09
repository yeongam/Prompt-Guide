# Security Review

- Slug: `security-review`
- Command: `/security-review`
- Version: 2.1.138
- Source: https://github.com/anthropics/claude-code  (commit `831608a36051`)
- Trigger: user asks security audit of pending branch changes

## Output

OWASP-focused risk-ranked findings from pending diffs

## Procedure

1. Confirm user intent matches skill trigger.
2. Execute skill command with minimal arguments.
3. Return only decision-critical output.
4. Skip background context already visible in session.

## Token Policy

- Return only decision-critical output.
- Omit redundant background context.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

# Code Review

- Slug: `code-review`
- Cmd: `/review | /security-review | /code-review`
- Source: https://github.com/anthropics/claude-code
- Source branch: `main`
- Catalog version: `2.1.161`
- Trigger: user asks to review PR, branch, or security audit of pending changes

## Procedure

1. Multi-pass review: logic correctness, style, security, tests.
2. OWASP-focused audit for /security-review.
3. Report findings as inline PR comments when --comment used.
4. Apply fixes when --fix used.
5. Effort levels control finding coverage breadth.

## Output

Risk-ranked list of findings with file:line references.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

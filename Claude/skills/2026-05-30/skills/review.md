# Review

- Slug: `review`
- Cmd: `/review`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to review PR or branch

## Procedure

1. Fetch diff against base branch.
2. Pass 1 — logic/correctness.
3. Pass 2 — style and naming.
4. Pass 3 — security (OWASP Top 10).
5. Pass 4 — test coverage gaps.
6. Output risk-ranked findings.

## Output

Ranked findings list: CRITICAL / HIGH / MEDIUM / LOW.

## Token Policy

- Return ranked list only; no verbose file reprints.
- Link to diff line numbers.
- Skip LOW findings if count > 10.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

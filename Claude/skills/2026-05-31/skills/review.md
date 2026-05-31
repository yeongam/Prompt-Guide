# review

- Slug: `review`
- Cmd: `/review`
- Source: https://github.com/anthropics/claude-code
- Trigger: User asks to review PR or branch.

## Procedure

1. Fetch diff (branch vs base or PR number).
2. Multi-pass: logic → style → security → tests.
3. Output risk-ranked findings with file:line refs.

## Output

Numbered findings list; severity HIGH/MED/LOW.

## Token Policy

- Diff only; skip unrelated context.
- Batch findings per file.

## Compatibility

- Works with local branch or GitHub PR number.

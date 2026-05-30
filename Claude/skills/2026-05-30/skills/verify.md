# Verify

- Slug: `verify`
- Cmd: `/verify`
- Source: https://github.com/anthropics/claude-code
- Trigger: user asks to verify a fix works, confirm a feature works, check a change manually

## Procedure

1. Identify the change to verify (PR, commit, or current working tree).
2. Start dev server or run CLI.
3. Test golden path end-to-end.
4. Test at least one edge case.
5. Monitor for regressions in adjacent features.
6. Report pass/fail with evidence.

## Output

Pass/Fail; exact command used; edge cases tested; any regressions found.

## Token Policy

- Report result and evidence only; no startup log verbosity.
- Include screenshot path if visual.
- One-line per test case.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

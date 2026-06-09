# Verify

- Slug: `verify`
- Source: anthropics/claude-code (built-in skill)
- Trigger: User wants to confirm a fix works, test a change manually, or validate local changes before pushing.

## Procedure

1. Run the app or relevant tests against the specific change.
2. Test the exact scenario described in the fix or feature.
3. Check for regressions in related functionality.
4. Report pass/fail with observed output.

## Output

Binary pass/fail with one-line evidence per tested case.

## Token Policy

- Pass cases: one line each.
- Failures: include reproduction steps and observed vs expected.

## Compatibility

- Complements `/run` (broader) vs. verify (targeted).
- No conflict with existing skills.

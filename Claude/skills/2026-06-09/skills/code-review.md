# Code Review

- Slug: `code-review`
- Source: anthropics/claude-code v2.1.169
- Trigger: User asks to review current diff for bugs, correctness issues, or code quality.

## Procedure

1. Use `/code-review [--comment|--fix] [low|medium|high|max]` to review pending changes.
2. `--comment`: Post findings as inline PR comments.
3. `--fix`: Apply findings directly to the working tree.
4. Effort levels: low/medium = high-confidence findings only; high/max = broader coverage.

## Output

Ranked list of findings with file:line references. Optionally applied or posted as comments.

## Token Policy

- Return only actionable findings.
- Skip no-issue confirmations; silence = clean.
- Link file:line rather than quoting full blocks.

## Compatibility

- Added: v2.1.169 (replaces/supersedes `/simplify` for bug-finding use case)
- `/simplify` remains for cleanup-only operations.
- No conflict with existing review flow.

# Simplify (Refactor)

- Slug: `simplify`
- Command: `/simplify`
- Trigger: user asks to clean up or refactor changed code
- Source: https://github.com/anthropics/claude-code

## Description

Review changed code for reuse, quality, efficiency; fix issues found

## Procedure

1. Diff changed files.
2. Identify: dead code, duplication, premature abstraction, unclear names.
3. Apply fixes in-place; do not introduce new abstractions.
4. Run type check and tests after edits.

## Output

Cleaned code with no behavior changes; brief summary of changes.

## Token Policy

- Show only modified hunks, not full file.
- One-line explanation per change.

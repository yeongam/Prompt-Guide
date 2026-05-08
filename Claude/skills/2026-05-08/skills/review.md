# PR Review

- Slug: `review`
- Command: `/review`
- Trigger: user asks to review PR or branch changes
- Source: https://github.com/anthropics/claude-code

## Description

Multi-pass PR review: logic, style, security, test coverage

## Procedure

1. Fetch diff vs base branch.
2. Pass 1: correctness and logic errors.
3. Pass 2: style and naming consistency.
4. Pass 3: security (OWASP top 10, injection, auth).
5. Pass 4: test coverage gaps.
6. Output risk-ranked findings, not exhaustive lists.

## Output

Prioritized finding list with file:line references.

## Token Policy

- Group findings by severity; skip trivial nits.
- One sentence per finding; link to relevant docs if needed.

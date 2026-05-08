# Security Review

- Slug: `security-review`
- Command: `/security-review`
- Trigger: user asks for security audit of current branch changes
- Source: https://github.com/anthropics/claude-code

## Description

OWASP-focused audit of pending diffs; outputs risk-ranked findings

## Procedure

1. Diff current branch vs main.
2. Check: injection (SQL/cmd/XSS), auth bypass, secrets in code, IDOR.
3. Rate each finding: Critical / High / Medium / Low.
4. Suggest minimal fix per finding.

## Output

Risk-ranked security findings with fix suggestions.

## Token Policy

- Skip Low findings if count > 5; summarize instead.
- No boilerplate OWASP definitions—assume reader knows them.

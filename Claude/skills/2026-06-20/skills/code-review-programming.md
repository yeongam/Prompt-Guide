# Code Review Programming

**Trigger:** PR review, logic audit, style checks, test coverage review

## Procedure
1. Run `/review` for standard multi-pass PR review
2. Run `/security-review` for OWASP-focused diff audit
3. Run `/simplify` for post-review cleanup pass
4. Flag logic errors before style issues
5. Include test coverage gaps in findings

## Token Policy
- Return only finding + fix pairs
- Skip informational items unless explicitly requested
- Rank by severity: Critical > High > Medium > Low

## Skill Commands
- `/review` — multi-pass PR review
- `/simplify` — refactor/cleanup pass
- `/security-review` — security-focused audit

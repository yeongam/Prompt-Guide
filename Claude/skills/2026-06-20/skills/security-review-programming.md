# Security Review Programming

**Trigger:** OWASP-focused security audits of code changes or new features

## Procedure
1. Run `/security-review` on current branch diffs
2. Check injection, auth, data exposure issues first
3. Rank: Critical > High > Medium > Low
4. Provide minimal code fix for each Critical/High finding
5. Verify fix does not introduce regression

## Token Policy
- Return finding + severity + one-line fix only
- Omit Low findings unless explicitly requested
- Skip repeated OWASP background

## Skill Command
`/security-review`

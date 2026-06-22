---
name: Claude Code Security Review
slug: claude-code-security-review
cmd: /security-review
version: 2.1.185
trigger: Use when user asks for a security audit, vulnerability scan, or OWASP check of pending changes.
---

OWASP-focused audit of current branch diffs; outputs risk-ranked findings.

**Procedure:**
1. Identify all changed files touching auth, input handling, DB, or network
2. Check injection vectors (SQL, command, XSS, SSRF)
3. Validate auth/authz logic and token handling
4. Scan for secrets or credentials in code
5. Report findings ranked by severity (Critical > High > Medium > Low)

**Output:** Risk-ranked finding list with remediation steps.

**Token policy:** Output findings only; omit clean-pass commentary.

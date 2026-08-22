# Security Review

- Slug: `security-review`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source commit: `5cfc0a1905ce`
- Source version: 2.1.240
- Trigger: User asks for a security audit of pending changes.

## Procedure

1. Scope to the current branch's pending diff.
2. Check for OWASP top-10 classes: injection, auth, XSS, SSRF, secrets.
3. Rank findings by exploitability and blast radius.
4. Skip theoretical issues with no reachable path.

## Output

Risk-ranked security findings for the pending diff.

## Token Policy

- No repeated background context across turns.
- Return decision-critical output only.
- Reference the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

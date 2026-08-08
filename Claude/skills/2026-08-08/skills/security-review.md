# Security Review

- Slug: `security-review`
- Source: session skill catalog, cross-checked 2026-08-08 (not itself named in the 2.1.129→2.1.226 delta)
- Trigger: User asks for a security audit of the pending changes on the current branch.

## Procedure

1. Scope to the pending diff on the current branch only.
2. Check against OWASP-class categories (injection, XSS, auth, secrets, etc.).
3. Rank findings by risk before reporting.

## Output

Risk-ranked security findings for the current branch's diff.

## Token Policy

- Findings only; skip restating the full diff.
- One line per finding unless severity requires more.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

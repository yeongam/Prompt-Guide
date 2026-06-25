# security-review

**cmd:** `/security-review`
**trigger:** user asks security audit of current branch changes
**desc:** OWASP-focused audit of pending diffs; outputs risk-ranked findings

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.
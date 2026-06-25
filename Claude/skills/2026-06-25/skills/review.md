# review

**cmd:** `/review`
**trigger:** user asks to review PR or branch
**desc:** Multi-pass PR review; checks logic, style, security, tests

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.
# simplify

**cmd:** `/simplify`
**trigger:** user asks to clean up or refactor changed code
**desc:** Review changed code for reuse/quality/efficiency, then fix issues

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.
# undo

**cmd:** `/undo`
**trigger:** user wants to undo last action
**desc:** Alias for /rewind; undoes last assistant action

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.
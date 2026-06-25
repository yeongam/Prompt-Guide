# focus

**cmd:** `/focus`
**trigger:** user wants compact view of conversation
**desc:** Toggle focus view showing only: prompt + tool summary + final response

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.
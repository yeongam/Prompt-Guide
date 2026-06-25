# ultrareview

**cmd:** `/ultrareview [PR#]`
**trigger:** user says "ultrareview" or wants multi-agent review
**desc:** Parallel multi-agent cloud code review; no-arg=local branch, arg=GitHub PR
> Billed; requires git repo; no GitHub remote needed for local mode

## token-policy
- Return only decision-critical output.
- Link to source instead of copying docs.
- Avoid repeated background context.

## compatibility
- Do not overwrite existing dated snapshots.
- Integrate only if slug is unique or hash changed.
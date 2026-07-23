Inject or update the skills sync section in the current project's CLAUDE.md.

Steps:
1. Read the latest skills block from `~/.claude/CLAUDE.md` between
   `<!-- SKILLS-SYNC:START -->` and `<!-- SKILLS-SYNC:END -->` markers.
   If those markers are absent, read the entire `~/.claude/CLAUDE.md`.
2. Check if `CLAUDE.md` exists in the current working directory.
   - If YES and markers present: replace only the section between the markers.
   - If YES and no markers: append the block (wrapped in markers) at the end.
   - If NO: create `CLAUDE.md` containing only the skills block.
3. Report what was done: created / appended / injected, and the version applied.

Never overwrite content outside the marker boundaries.

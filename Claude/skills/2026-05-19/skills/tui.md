# TUI Mode

- Slug: `tui`
- Cmd: `/tui`
- Source: https://github.com/anthropics/claude-code
- Source commit: `unknown`
- Catalog version: `2.1.143`
- Trigger: Rendering looks flickery or user wants full-screen mode

## Procedure

1. Confirm trigger matches user intent before invoking.
2. Prefer smallest effective invocation.
3. Keep output scoped to the specific request.
4. Do not add unrequested features or refactors.
5. Verify result without re-reading unchanged files.

## Output

Switch to flicker-free alt-screen TUI rendering

## Token Policy

- Avoid repeating background context already in conversation.
- Return only decision-critical output.
- Link to source instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every update.

## Notes

- Also: CLAUDE_CODE_NO_FLICKER env var

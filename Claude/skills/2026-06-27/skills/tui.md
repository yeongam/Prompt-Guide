# /tui — tui

- Category : `ux`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: rendering looks flickery or user wants full-screen mode.

**Action** : Switch to flicker-free alt-screen TUI rendering.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

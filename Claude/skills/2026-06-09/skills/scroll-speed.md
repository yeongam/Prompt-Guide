# Scroll Speed

- Slug: `scroll-speed`
- Source: anthropics/claude-code v2.1.169
- Trigger: User wants to adjust mouse wheel scroll speed in the TUI renderer.

## Procedure

1. Use `/scroll-speed <value>` to set scroll speed.
2. Live preview updates immediately.
3. Setting is persisted in user config.

## Output

Confirmation of new scroll speed with live preview.

## Token Policy

- One-liner confirmation only.

## Compatibility

- Added: v2.1.169
- Only relevant in TUI/fullscreen mode (`/tui`).

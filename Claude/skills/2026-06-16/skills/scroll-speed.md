# /scroll-speed — Mouse Scroll Speed

- Slug: `scroll-speed`
- Cmd: `/scroll-speed [value]`
- Added: v2.1.139
- Trigger: User wants to adjust mouse-wheel scroll speed in fullscreen TUI mode.

## Procedure

1. `/scroll-speed` without args: opens live-preview slider.
2. `/scroll-speed <n>`: set speed directly (1–10).
3. Also: set `wheelScrollAccelerationEnabled: false` in settings.json to disable acceleration.

## Output

Scroll speed updated with live preview.

## Token Policy

- One-line confirmation of new value.

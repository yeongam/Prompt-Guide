# Artifact Design Fundamentals

- Slug: `artifact-design`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: Loaded before writing any Artifact (HTML/Markdown) to calibrate design investment.

## Procedure

1. Load before the first line of artifact HTML/CSS is written.
2. Calibrate design effort to what the request actually warrants.
3. Apply theme-awareness (light/dark) and responsive layout rules.

## Output

An artifact whose design investment matches the task, styled for both themes.

## Token Policy

- Skip elaborate design passes for simple/utility artifacts.

## Compatibility

- Additive only; pairs with `artifact-capabilities`; no collision with existing entries.

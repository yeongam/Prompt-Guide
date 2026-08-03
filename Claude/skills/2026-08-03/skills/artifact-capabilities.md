# Artifact Runtime Capabilities

- Slug: `artifact-capabilities`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: An artifact needs live/connected data, shared state across viewers, or self-updating behavior — load before declaring `capabilities` or writing `window.claude.*` code.

## Procedure

1. Load before passing any `capabilities` field to the Artifact tool.
2. Confirm which runtime capabilities are actually enabled for this user before relying on them.
3. Use the documented `window.claude.*` call shapes rather than improvising an API surface.

## Output

An artifact correctly declaring and using only supported runtime capabilities.

## Token Policy

- Load only when the task genuinely needs runtime behavior beyond static HTML.

## Compatibility

- Additive only; pairs with `artifact-design`; no collision with existing entries.

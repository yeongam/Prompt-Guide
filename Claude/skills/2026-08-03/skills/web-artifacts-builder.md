# Web Artifacts Builder

- Slug: `web-artifacts-builder`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: Building complex claude.ai HTML artifacts needing state management, routing, or shadcn/ui — not simple single-file HTML/JSX.

## Procedure

1. Confirm complexity actually warrants React/Tailwind/shadcn vs. a plain single-file artifact.
2. Structure state/routing before adding UI polish.
3. Keep the artifact self-contained per Artifact-tool constraints (no external CDN/network calls).

## Output

A working multi-component web artifact.

## Token Policy

- Reuse shadcn/ui primitives instead of hand-rolling equivalents.

## Compatibility

- Additive only; no collision with existing catalog entries.

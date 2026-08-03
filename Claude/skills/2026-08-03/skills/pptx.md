# PowerPoint Deck Authoring

- Slug: `pptx`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: Creating, reading, editing, or combining `.pptx`/`.potx` slide decks, templates, layouts, speaker notes, or comments.

## Procedure

1. Identify read/extract vs edit vs create-from-scratch.
2. Respect existing template/layout/master-slide conventions when editing.
3. Keep speaker notes and comments intact unless asked to change them.
4. Verify the deck opens correctly before delivering.

## Output

A valid `.pptx`/`.potx` deliverable matching the request.

## Token Policy

- Operate via helper scripts rather than inlining full slide XML.

## Compatibility

- Additive only; no collision with existing catalog entries.

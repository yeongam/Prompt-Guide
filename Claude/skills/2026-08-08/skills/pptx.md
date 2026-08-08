# PPTX (Slide Decks)

- Slug: `pptx`
- Source: session skill catalog, cross-checked 2026-08-08 (not itself named in the 2.1.129→2.1.226 delta)
- Trigger: A .pptx/.potx file is input or output — create, read, edit, combine, or split a deck.

## Procedure

1. Auto-triggers on "deck", "slides", "presentation", or a .pptx/.potx filename.
2. Handle layouts, templates, speaker notes, and comments as needed.
3. Extracted content destined elsewhere (e.g. an email summary) still routes through this skill if the source is a deck.

## Output

A slide deck, or extracted/restructured content from one.

## Token Policy

- Manipulate the file directly rather than round-tripping full content through the conversation.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

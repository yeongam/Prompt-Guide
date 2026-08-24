# PDF

- Slug: `pdf`
- Category: documentation
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: user wants to create, read, merge, split, or otherwise manipulate a PDF

## Procedure

1. Extract text/tables/images or assemble the requested PDF operation.
2. Handle forms, watermarks, encryption, or OCR as requested.

## Output

The resulting PDF file or extracted content.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# DOCX (Word Documents)

- Slug: `docx`
- Source: session skill catalog, cross-checked 2026-08-08 (not itself named in the 2.1.129→2.1.226 delta)
- Trigger: A .docx/.dotx file is input or output — create, read, edit, or reorganize a Word document/template.

## Procedure

1. Auto-triggers whenever a .docx/.dotx file is touched, by name or by task shape ("report", "memo", "letter").
2. Handle TOC, headings, page numbers, letterheads, tracked changes, and comments as needed.
3. Do not use for PDFs, spreadsheets, or unrelated coding tasks.

## Output

A polished Word document, or extracted/reorganized content from one.

## Token Policy

- Manipulate the file directly rather than round-tripping full content through the conversation.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

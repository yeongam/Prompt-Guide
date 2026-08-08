# PDF

- Slug: `pdf`
- Source: session skill catalog, cross-checked 2026-08-08 (not itself named in the 2.1.129→2.1.226 delta)
- Trigger: Any task involving .pdf files.

## Procedure

1. Auto-triggers on mention of a .pdf file or a request to produce one.
2. Cover extraction (text/tables), merge/split/rotate, forms, watermarking, encryption, and OCR of scanned PDFs.

## Output

A produced/modified PDF, or extracted content from one.

## Token Policy

- Manipulate the file directly rather than round-tripping full content through the conversation.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

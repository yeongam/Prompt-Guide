# PDF Manipulation

- Slug: `pdf`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: Reading/extracting, merging, splitting, rotating, watermarking, form-filling, encrypting, or OCR'ing PDF files.

## Procedure

1. Determine operation type (extract, merge/split, form-fill, OCR, security).
2. For large PDFs, page-range reads instead of whole-file loads.
3. Confirm output PDF is valid and matches the requested transformation.

## Output

A correctly transformed or extracted PDF result.

## Token Policy

- Use page ranges and targeted extraction; avoid dumping full PDF text into context.

## Compatibility

- Additive only; no collision with existing catalog entries.

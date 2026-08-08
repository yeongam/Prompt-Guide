# XLSX (Spreadsheets)

- Slug: `xlsx`
- Source: session skill catalog, cross-checked 2026-08-08 (not itself named in the 2.1.129→2.1.226 delta)
- Trigger: A spreadsheet (.xlsx/.xlsm/.xltx/.csv/.tsv) is the primary input or output.

## Procedure

1. Auto-triggers whenever a spreadsheet file is referenced by name/path or is the deliverable shape.
2. Handle formulas, formatting, charts, and cleanup of malformed tabular data.
3. Do not use when the deliverable is a Word doc, HTML report, or database pipeline instead.

## Output

A spreadsheet file (new, edited, or converted from other tabular data).

## Token Policy

- Manipulate the file directly rather than round-tripping full content through the conversation.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

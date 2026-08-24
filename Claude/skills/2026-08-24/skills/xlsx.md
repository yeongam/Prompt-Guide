# XLSX

- Slug: `xlsx`
- Category: documentation
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.241`
- Trigger: user wants to create, read, or edit a spreadsheet (.xlsx/.csv/.tsv)

## Procedure

1. Read or scaffold sheets, formulas, and formatting.
2. Apply requested edits, cleaning, or chart generation.

## Output

A created or edited spreadsheet file.

## Token Policy

- One-line description; expand only when the user's phrasing is ambiguous.
- Reuse this catalog instead of restating skill behavior inline.
- Prefer the narrowest applicable skill over general-purpose exploration.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

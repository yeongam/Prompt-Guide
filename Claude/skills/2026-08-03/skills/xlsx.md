# Spreadsheet Authoring

- Slug: `xlsx`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: Opening, editing, or creating `.xlsx`/`.xlsm`/`.csv`/`.tsv` files — formulas, formatting, charts, data cleaning.

## Procedure

1. Determine if the deliverable must remain a spreadsheet (in scope) vs. a report/doc (out of scope for this skill).
2. Preserve existing formulas/formatting unless the task requires changing them.
3. Validate computed values and chart references after edits.

## Output

A correct, properly formatted spreadsheet file.

## Token Policy

- Avoid dumping full sheet contents into context; sample and target ranges instead.

## Compatibility

- Additive only; no collision with existing catalog entries.

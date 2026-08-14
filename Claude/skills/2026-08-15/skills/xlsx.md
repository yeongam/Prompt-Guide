# xlsx

- Slug: `xlsx`
- Source: https://github.com/anthropics/skills/tree/main/skills/xlsx
- Source commit: `ref:main`
- Trigger: Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: open, read, edit, or fix an existing .xlsx, .xlsm, .xltx, .csv, or .tsv file (e.g., adding columns, computing formulas,.

## Output

Compact, repeatable instructions for the task the skill covers.

## Token Policy

- Reference the upstream SKILL.md instead of copying its full body.
- Keep the local card to trigger + one-line output + policy notes.
- Load full skill content only when the skill actually fires.

## Compatibility

- Namespaced separately from Claude Code slash-command skills.
- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

## Source Summary

# XLSX creation, editing, and analysis | Task | Approach | |---|---| | **Create** or **edit** with formulas/formatting | `openpyxl` — see gotchas below | | **Bulk data** in or out | `pandas` (`read_excel`, `to_excel`) | | **Quick look** at a sheet | `markitdown file.xlsx` — `## SheetName` per sheet; reads `.xlsm` too. No cell coordinates, so don't plan edits from it | | **Read** a model (formulas *and* values) | two.

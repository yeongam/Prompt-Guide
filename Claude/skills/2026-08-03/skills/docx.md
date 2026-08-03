# Word Document Authoring

- Slug: `docx`
- Source: Claude Code built-in skill (session skill listing, captured 2026-08-03)
- Trigger: Creating, reading, or editing `.docx`/`.dotx` files — reports, letters, templates, tracked changes, comments.

## Procedure

1. Identify whether the task is read/extract, edit-in-place, or create-from-scratch.
2. For edits, preserve existing formatting, styles, and tracked-changes state.
3. For new documents, apply headings/TOC/page numbers as requested, not by default.
4. Verify output opens cleanly (no corrupted XML) before handing back.

## Output

A valid, correctly formatted `.docx`/`.dotx` deliverable.

## Token Policy

- Do not paste full document XML into context; operate via the skill's helper scripts.

## Compatibility

- Additive only; no collision with existing catalog entries.

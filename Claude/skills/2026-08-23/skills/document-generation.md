# Document Generation

- Slug: `document-generation`
- Category: documentation
- Source: https://github.com/anthropics/claude-code
- Source commit: `5cfc0a1905ce`
- Source version: 2.1.240
- Trigger: Task requires producing or editing docx, pdf, pptx, or xlsx files.

## Procedure

1. Match the skill to the target file type (docx/pdf/pptx/xlsx).
2. Preserve existing formatting and structure when editing.
3. Read files fully before summarizing or redistributing them.

## Output

Generated or edited office document matching the requested format.

## Token Policy

- No repeated background context across turns.
- Return decision-critical output only.
- Reference the source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

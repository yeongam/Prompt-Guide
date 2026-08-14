# pdf

- Slug: `pdf`
- Source: https://github.com/anthropics/skills/tree/main/skills/pdf
- Source commit: `ref:main`
- Trigger: Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating.

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

# PDF Processing Guide ## Overview This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see REFERENCE.md. If you need to fill out a PDF form, read FORMS.md and follow its instructions. ## Quick Start ## Python Libraries ### pypdf - Basic Operations #### Merge PDFs #### Split PDF #### Extract Metadata #.

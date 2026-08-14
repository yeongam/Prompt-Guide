# docx

- Slug: `docx`
- Source: https://github.com/anthropics/skills/tree/main/skills/docx
- Source commit: `ref:main`
- Trigger: Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) or Word templates (.dotx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', '.dotx', or requests to produc.

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

# DOCX creation, editing, and analysis A `.docx` is a ZIP archive of XML files. Choose your approach by task: | Task | Approach | |---|---| | **Create** a new document | Write a `docx` (npm) script — see gotchas below | | **Edit** an existing document | `unzip` → edit `word/document.xml` → `zip` (docx-js cannot open existing files) | | **Read** content | `pandoc -t markdown file.docx` | > Script paths below are rela.

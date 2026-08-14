# pptx

- Slug: `pptx`
- Source: https://github.com/anthropics/skills/tree/main/skills/pptx
- Source commit: `ref:main`
- Trigger: Use this skill any time a .pptx or .potx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx or .potx file (even i.

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

# PPTX creation, editing, and analysis A `.pptx` is a ZIP archive of XML files. Choose your approach by task: | Task | Approach | |---|---| | **Create** a new deck | Write a `pptxgenjs` script — see gotchas below | | **Edit** an existing deck, or build from a template | unzip → edit `ppt/slides/slideN.xml` → zip | | **Read** content | `markitdown deck.pptx` (one block per slide under ` ` markers); visual grid: `pyth.

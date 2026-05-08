# Documentation Maintenance

- Slug: `documentation-maintenance`
- Trigger: user asks to update docs, READMEs, or developer guides
- Source: https://github.com/anthropics/claude-code

## Description

Keep docs in sync with code; traceable to source commits

## Procedure

1. Identify docs that reference changed APIs or behavior.
2. Update examples to match current code signatures.
3. Preserve source-traceability (link to commit or PR).
4. Keep docs under 80 chars/line; no filler sentences.

## Output

Updated doc files with diff summary.

## Token Policy

- Omit unchanged sections from output.
- Link to external references rather than copying content.

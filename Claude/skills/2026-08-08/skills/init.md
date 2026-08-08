# Init

- Slug: `init`
- Source: session skill catalog, cross-checked 2026-08-08 (not itself named in the 2.1.129→2.1.226 delta)
- Trigger: User asks to initialize or document a codebase.

## Procedure

1. Survey codebase architecture, conventions, and common commands.
2. Generate CLAUDE.md capturing what a new contributor/agent needs.
3. Per `/doctor` guidance (added this delta): prefer content Claude can't easily re-derive from the codebase itself — avoid bloating CLAUDE.md with restatable detail.

## Output

A CLAUDE.md file at the repo root.

## Token Policy

- Keep CLAUDE.md itself lean; it is read on every future session.
- Do not duplicate content easily discoverable by grep/read.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

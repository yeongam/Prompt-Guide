# Ultrareview (Multi-Agent Review)

- Slug   : `ultrareview`
- Source : https://github.com/anthropics/claude-code
- Version: 2.1.129
- Trigger: user says 'ultrareview' or wants multi-agent cloud review
- Note   : Billed; requires git repo; no GitHub remote needed for local mode.

## Procedure

1. Run /ultrareview [PR#] or no arg for local branch.
2. Parallel agents review logic/style/security/tests.
3. Aggregate ranked findings.

## Output

Parallel multi-agent review report.

## Token Policy

- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

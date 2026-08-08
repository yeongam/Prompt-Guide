# Simplify

- Slug: `simplify`
- Source: session skill catalog, cross-checked 2026-08-08 (not itself named in the 2.1.129→2.1.226 delta)
- Trigger: User asks to clean up or refactor changed code.

## Procedure

1. Review changed code only, for reuse/simplification/efficiency/altitude issues.
2. Do not hunt for correctness bugs — that is `/code-review`'s job.
3. Apply the fixes directly rather than just reporting them.

## Output

Cleaned-up diff; no separate findings report.

## Token Policy

- Quality-only pass; skip restating unrelated code.
- No duplicate explanation of what `/code-review` already covers.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

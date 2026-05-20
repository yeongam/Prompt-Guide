# UltraReview

- Slug: `ultrareview`
- Cmd: `/ultrareview [PR#]`
- Source: anthropics/claude-code v2.1.145
- Trigger: user says ultrareview or wants multi-agent review

## Procedure

1. Determine target (local branch or PR#).
2. Spawn parallel review agents.
3. Merge findings.
4. Return ranked report.

## Output

Multi-agent review report with parallel findings merged.

## Token Policy

- Return merged report only, not per-agent transcripts.
- Billed; note cost estimate before starting.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

# Investigate

- Slug: `investigate`
- Command: `/investigate`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants root cause of incident or puzzling behavior

## Description

Parallel hypotheses, adversarial refutation, root-cause report

## Procedure

1. Collect evidence: logs, traces, diffs.
2. Generate competing hypotheses in parallel.
3. Adversarially refute each.
4. Write root-cause report with fix suggestion.

## Output

Root-cause report with evidence chain.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

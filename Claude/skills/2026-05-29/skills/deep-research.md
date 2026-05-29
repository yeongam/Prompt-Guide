# Deep Research

- Slug: `deep-research`
- Command: `/deep-research`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants multi-source fact-checked research report

## Description

Fan-out searches, fetch sources, adversarial verify, cited report

## Procedure

1. Fan out multiple search queries.
2. Fetch top sources.
3. Adversarially verify claims.
4. Synthesize cited report.

## Output

Cited research report.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical output.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

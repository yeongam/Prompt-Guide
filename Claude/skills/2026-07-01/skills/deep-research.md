# Deep Research

- Slug: `deep-research`
- Command: `/deep-research`
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.196`
- Source commit: `c80896ca84bd`
- Trigger: user wants multi-source fact-checked research

## Description

Fan-out web searches, fetch sources, adversarially verify claims, synthesize cited report

## Procedure

1. Check official source alignment first.
2. Prefer smallest working implementation.
3. Keep prompt and code paths short.
4. Verify with narrowest relevant command.
5. Link to source docs instead of copying long content.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

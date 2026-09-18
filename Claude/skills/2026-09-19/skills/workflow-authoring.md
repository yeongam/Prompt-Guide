# Workflow Authoring

- Slug: `workflow-authoring`
- Command: `workflow-authoring`
- Category: programming
- Source: https://github.com/anthropics/claude-code
- Source version: `2.1.276`
- Trigger: Reference for writing a Workflow tool script (agent/parallel/pipeline).

## Procedure

1. Load before authoring any Workflow script.
2. Follow the agent()/parallel()/pipeline() API and phase() layout.
3. Keep agent count within the session's size guideline.

## Output

A validated workflow script ready for the Workflow tool.

## Token Policy

- No duplicated background context between skills.
- Reference this catalog instead of re-explaining the skill inline.
- Keep procedure steps to the minimum needed to act.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve Claude/skills/SKILLS_CATALOG.yaml entries not covered here.

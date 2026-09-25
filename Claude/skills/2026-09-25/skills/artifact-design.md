# artifact-design

- Cmd: `(auto-trigger: before writing any artifact)`
- Source: https://github.com/anthropics/claude-code @ 2.1.282
- Trigger: writing any Artifact, including a skill-instructed Markdown one

## Desc

Design fundamentals and contract for Artifacts (fonts, theming, size limits)

## Token Policy

- Keep card to trigger + one-line desc; no upstream doc copies.
- Link to the official repo instead of inlining long guidance.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.

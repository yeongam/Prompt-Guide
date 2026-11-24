# Shared skill rules (applies to every card in this snapshot)

- Small sources are inlined verbatim (ready to run); larger ones are outline + `Src` link: read Src before acting.
- Token policy: no restated background, return only decision-critical output, prefer one batched tool call.
- Compatibility: core.yaml built-ins win on name clash; plugin cards are renamed `<plugin>-<name>`.
- Install a card: copy `<slug>/` to `.claude/skills/<slug>/` (SKILL.md is valid Claude Code skill format).

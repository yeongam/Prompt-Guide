# Claude Skill Routine

This directory holds Claude-focused skill artifacts plus archived Claude system prompts.

The routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It reads the official Anthropic plugin manifest (`anthropics/skills`) and the Claude Code
changelog (`anthropics/claude-code`), keeps only coding, programming, and documentation
skills, and writes compact cards into:

```text
Claude/skills/YYYY-MM-DD/skills/
```

Each snapshot carries one `.md` card per skill plus a `catalog.json` holding the skill
index, the shared `defaults` block, and the Claude Code CLI reference (slash commands,
hooks, settings, env vars). Shared boilerplate lives in `defaults` once instead of being
repeated per card.

The diff against the previous dated snapshot is written to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

The dedicated GitHub Actions workflow runs this routine daily at 00:00 KST and blocks
routine changes outside `Claude/`.

Remote GitHub Actions updates repository artifacts only. Applying them to a live local
Claude Code runtime still requires an explicit local sync or install step.

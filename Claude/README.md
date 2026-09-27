# Claude Skill and Hook Routine

This directory contains Claude-focused skill and hook artifacts.

`Claude/skills/SKILLS_CATALOG.yaml` is the hand-curated catalog of Claude Code's
own CLI features (skills, hooks, settings, env vars, models), updated from the
official changelog via `scripts/update_skills.py`. It is not touched by the
routine below.

The dated-snapshot routine entrypoint is:

```bash
python Claude/scripts/sync_claude_skills.py
```

It syncs compact skill and hook cards from official Anthropic GitHub
repositories into:

```text
Claude/skills/YYYY-MM-DD/skills/
Claude/hooks/YYYY-MM-DD/hooks/
```

It also writes a concise changelog to:

```text
Claude/Changelogs/YYYY-MM-DD.txt
```

Run daily, this mirrors the structure already used by `GPT/scripts/sync_openai_skills.py`
so both directories stay consistent. It only ever writes inside `Claude/` and
never modifies `GPT/` or `Gemini/`.

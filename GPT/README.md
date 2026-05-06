# GPT Skill and Hook Routine

This directory contains GPT-focused skill and hook artifacts only.

The routine entrypoint is:

```bash
python GPT/scripts/sync_openai_skills.py
```

It syncs compact skill and hook cards from official OpenAI GitHub repositories into:

```text
GPT/skills/YYYY-MM-DD/skills/
GPT/hooks/YYYY-MM-DD/hooks/
```

It also writes a concise changelog to:

```text
GPT/Changelogs/YYYY-MM-DD.txt
```

The dedicated GitHub Actions workflow runs this routine daily at 00:00 KST and blocks routine changes outside `GPT/`.

Remote GitHub Actions updates the repository artifacts only. Applying these artifacts to a live local Codex runtime still requires an explicit local sync or install step.

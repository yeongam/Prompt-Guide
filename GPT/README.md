# GPT Skill Routine

This directory contains GPT-focused skill artifacts only.

The routine entrypoint is:

```bash
python GPT/scripts/sync_openai_skills.py
```

It syncs compact skill cards from official OpenAI GitHub repositories into:

```text
GPT/skills/YYYY-MM-DD/skills/
```

It also writes a concise changelog to:

```text
GPT/Changelogs/YYYY-MM-DD.txt
```

Remote scheduling requires a GitHub Actions workflow outside `GPT/`. That workflow is intentionally not included here because the current allowed edit scope is `Prompt-Guide/GPT` only.

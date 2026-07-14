# Claude API Coding

- Slug: `claude-api-coding`
- Source: https://github.com/anthropics/claude-cookbooks
- Source commit: `content-hash:4ffad49fa541`
- Trigger: Use for implementing or debugging Claude API calls and examples.

## Procedure

1. Check official source alignment first.
2. Prefer smallest working implementation.
3. Use structured APIs over ad hoc parsing.
4. Keep prompt and code paths short.
5. Verify with the narrowest relevant command.

## Output

Small code-oriented checklist with official-example alignment.

## Token Policy

- Avoid repeated background context.
- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.
- Do not modify Claude/skills/SKILLS_CATALOG.yaml or .version.

## Source Summary

# Claude Cookbooks The Claude Cookbooks provide code and guides designed to help
developers build with Claude, offering copy-able code snippets that you can easily
integrate into your own projects. ## Prerequisites To make the most of the examples in
this cookbook, you'll need a Claude API key (sign up for free
[here](https://www.anthropic.com)). While the code examples are primarily written in
Python, the concepts.

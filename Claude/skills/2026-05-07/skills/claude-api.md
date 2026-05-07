# Claude API Programming

- Slug   : `claude-api`
- Source : https://github.com/anthropics/claude-code
- Version: 2.1.129
- Trigger: code imports anthropic SDK; user asks about Claude API features

## Procedure

1. Identify target model from task.
2. Enable prompt caching on static context blocks.
3. Use tool_use for structured output.
4. Reference official SDK for model migration.

## Output

Working Claude API integration with caching enabled.

## Models

| Role   | Model ID                        |
|--------|---------------------------------|
| opus   | `claude-opus-4-7`               |
| sonnet | `claude-sonnet-4-6`             |
| haiku  | `claude-haiku-4-5-20251001`     |

## Token Policy

- Return only decision-critical code or instructions.
- Link to source repo instead of copying long docs.
- Avoid repeated background context.

## Compatibility

- Do not overwrite existing dated skill snapshots.
- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

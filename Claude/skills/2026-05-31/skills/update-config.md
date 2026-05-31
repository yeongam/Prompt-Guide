# update-config

- Slug: `update-config`
- Cmd: `/update-config`
- Source: https://github.com/anthropics/claude-code
- Trigger: Automated behavior requests; hook, permission, env var changes.

## Procedure

1. Determine target: project or user settings.json.
2. Edit JSON: hooks, permissions, env vars.
3. Validate JSON syntax; show diff before applying.

## Output

Updated settings.json; summary of changes.

## Token Policy

- Read file once; patch only changed keys.

## Compatibility

- Supports PreToolUse, PostToolUse, Stop, Notification, PreCompact hooks.

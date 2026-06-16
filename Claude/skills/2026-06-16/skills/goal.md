# /goal — Set Completion Condition

- Slug: `goal`
- Cmd: `/goal <condition>`
- Added: v2.1.139
- Trigger: User wants Claude to work autonomously until a defined condition is met.

## Procedure

1. Define condition: e.g. `/goal all tests pass`.
2. Claude iterates until condition evaluates true.
3. Stops and reports when condition is met or becomes unresolvable.

## Output

Final state report: condition met / blocked with diagnosis.

## Token Policy

- Suppress intermediate status unless blocked.
- Single summary on completion.

# Goal Completion

- Slug: `goal-completion`
- Source: anthropics/claude-code v2.1.169
- Trigger: User wants to define a completion condition for Claude to work toward across multiple turns.

## Procedure

1. Use `/goal <description>` to set the goal.
2. Claude tracks progress toward the goal across turns autonomously.
3. Claude stops or reports when goal condition is met.
4. Suitable for long-running tasks (e.g., "get all tests green", "fix all lint errors").

## Output

Goal confirmation and ongoing progress updates per turn.

## Token Policy

- Report only delta progress per turn.
- Final report when goal is achieved.

## Compatibility

- Added: v2.1.169
- Complements `/loop` for recurring vs. one-shot completion goals.

# Loop

- Slug: `loop`
- Cmd: `/loop [interval] [/command]`
- Source: https://github.com/anthropics/claude-code
- Trigger: user wants a recurring task, polling, or repeated command on an interval

## Usage

```
/loop 5m /review          # run /review every 5 minutes
/loop 10m check deploy    # run prompt every 10 minutes (default interval)
```

## Procedure

1. Parse interval (s/m/h suffix; default 10m).
2. Parse command or prompt.
3. Run on interval until user stops.
4. Summarize each iteration result compactly.
5. Final summary on exit.

## Output

Per-iteration: one-line status. Final: summary table.

## Token Policy

- Minimal per-iteration output.
- Summarize accumulated results on completion.
- No redundant context re-injection each iteration.

## Compatibility

- Integrate only if slug is unique or content hash changed.
- Preserve changelog evidence for every generated update.

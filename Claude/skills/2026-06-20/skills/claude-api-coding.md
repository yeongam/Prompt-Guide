# Claude API Coding

**Trigger:** Implementing or debugging Anthropic SDK / Claude API calls

## Models (2026-06-20)
| Alias | Model ID |
|-------|----------|
| fable | `claude-fable-5` |
| opus | `claude-opus-4-8` |
| sonnet | `claude-sonnet-4-6` |
| haiku | `claude-haiku-4-5-20251001` |

## Procedure
1. Check official source alignment first
2. Prefer smallest working implementation
3. Use structured tool-use APIs over ad hoc parsing
4. Apply prompt caching (`cache_control`) where response is reused
5. Verify with the narrowest relevant command

## Token Policy
- Return only decision-critical code
- Link to source instead of copying long docs
- Avoid repeated background context in multi-turn calls

## Key Patterns
```python
# Minimal SDK call
from anthropic import Anthropic
client = Anthropic()
msg = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Skill Command
`/claude-api`

# claude-api | /claude-api
use: code imports anthropic SDK; Claude API/pricing/model questions
do: read skill before editing file; never answer model/pricing from memory
sub: upgrade (py anthropic 0.x->1.x; Timeout=anthropic.Timeout) | prompt-audit | managed-agents-secure (read-only) | OTel tracing (ant CLI)
models: claude-fable-5-1 claude-opus-5-5 claude-sonnet-5-5 claude-haiku-5-5
out: minimal diff; cache prompts; no repeated context

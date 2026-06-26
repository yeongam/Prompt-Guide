# /ultrareview [PR#] — ultrareview

- Category : `advanced`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user says "ultrareview" or wants multi-agent review.

**Action** : Parallel multi-agent cloud code review (local branch or GitHub PR).

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

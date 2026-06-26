# /add-dir — add-dir

- Category : `utility`
- Source   : https://github.com/anthropics/claude-code @ `f0919a1a7277`
- Version  : 2.1.193

**Trigger**: user wants to add a directory to the session context.

**Action** : Add directory to Claude Code session search scope.

## Token Policy

- Use cmd directly; avoid restating background context.
- Return only decision-critical output.
- Link to source over inline documentation.

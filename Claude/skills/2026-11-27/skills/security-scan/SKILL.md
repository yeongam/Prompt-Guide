---
name: security-scan
description: Security scan of repo/diff/commit, threat model, triage SARIF findings, or patch suggestions. Use on "security scan", "threat model", "audit for vulns".
---
# Security Scan
Src: claude-plugins-official/{claude-security,security-guidance}@0fbfda5a91f4
Prefer built-in `/security-review` for branch diffs. Modes:
- scan: whole repo or scoped path → ranked findings (sev, file:line, exploit path, fix).
- changes: branch/PR/commit diff only.
- triage: verify existing SARIF/report items against code; mark real/false.
- patch: one targeted patch per confirmed finding; never auto-apply.
- threat-model: assets, entry points, trust boundaries, top threats; update in place.
Edit-time guard: flag eval/exec, shell injection, unsafe deserialization, innerHTML/XSS, hardcoded secrets.

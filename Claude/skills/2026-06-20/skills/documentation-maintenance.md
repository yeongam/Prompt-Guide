# Documentation Maintenance

**Trigger:** Updating CLAUDE.md, READMEs, changelogs, or developer guides

## Procedure
1. Run `/init` to generate baseline CLAUDE.md if missing
2. Keep descriptions under one line per entry
3. Link to source rather than copying long content
4. Remove stale entries before adding new ones
5. Verify final doc renders correctly

## Token Policy
- Omit boilerplate; reference canonical source
- Return only decision-critical instructions
- Avoid repeated background context

## Naming Rules
- Changelogs: `YYYY-MM-DD.txt` in `Changelogs/` directory
- Skill snapshots: `YYYY-MM-DD/skills/` dated directories
- One file per skill; slug matches filename

## Skill Command
`/init` — generates CLAUDE.md

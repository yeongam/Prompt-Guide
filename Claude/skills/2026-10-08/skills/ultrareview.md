# ultrareview (/ultrareview [PR#])
Use: multi-agent cloud review (billed). No arg=local branch, arg=GitHub PR.
- Local upload needs git>=2.31; refuses symbolic-ref branch, --separate-git-dir, no base branch.
- May upload uncommitted tracked-file changes; key files (id_rsa, kubeconfig) stay local.
- CLI: claude ultrareview. Stop via /tasks (x, confirms).

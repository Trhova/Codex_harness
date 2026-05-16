# Codex App and Cloud

The Codex app/cloud workflow is useful when you want task-oriented repository work that can be reviewed separately from a local terminal session.

Use the app/cloud workflow for:

- issue-sized changes
- PR review and follow-up
- background investigation
- documentation review
- tasks where local machine state is not required

Use the CLI when the task depends on:

- local files not pushed to Git
- local credentials
- local services
- interactive terminal debugging
- machine-specific install state

## Prompt Shape

Give the same information you would give a senior engineer:

```text
Goal:
Make the harness docs clear for new users.

Constraints:
- Do not change installer behavior.
- Keep examples generic.
- Do not include secrets or private paths.
- Prefer official Codex docs for current behavior.

Verification:
- Run git diff --check.
- Summarize docs changed and any commands run.
```

## Keep Context Small

Point Codex at the right files:

```text
Start with README.md, docs/README.md, scripts/harness.py, and docs/rollback.md.
Do not scan vendor/ unless needed.
```

For this repo, also say:

```text
If graphify-out/GRAPH_REPORT.md exists, read it first. It may be noisy because vendor dependencies are present, so verify important claims against README.md and scripts/harness.py.
```

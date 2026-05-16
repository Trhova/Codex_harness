# Concepts

## What Codex Is

Codex is an agentic coding assistant. In the CLI it can read files, edit files, run commands, inspect diffs, and help carry a change through verification. In app/cloud workflows it can work on repository tasks with a more remote, review-oriented flow.

You get the best results when the repository tells Codex how to work: what commands are safe, where docs live, how tests run, what not to touch, and what output should be summarized.

## What This Harness Adds

Codex Harness installs local support around Codex:

- RTK for compact command output.
- Graphify for repository structure reports.
- Codex instructions so future sessions know when to use those tools.
- Rollback tracking for files changed by the harness.

## What RTK Is

RTK is a command wrapper. It is useful when a raw command would produce too much output or output that is hard for Codex to scan.

Use RTK for commands such as:

```bash
rtk git status
rtk git diff
rtk grep "search term"
rtk find . -type f
rtk pytest
```

RTK does not replace every shell command. For tiny commands, raw shell output is fine.

## What Graphify Is

Graphify builds repository artifacts under `graphify-out/`, especially `GRAPH_REPORT.md`. That report gives Codex a structured starting point for architecture, ownership, communities, and important files.

Use Graphify before broad questions such as:

- Where is this feature implemented?
- What modules are related?
- What should a new contributor read first?
- Which files are likely affected by this change?

## What AGENTS.md Is

`AGENTS.md` is a durable instruction file for Codex. A global file under `~/.codex/AGENTS.md` can describe your general preferences. A project-level `AGENTS.md` should describe repository-specific rules.

Good project instructions include:

- preferred commands
- test commands
- formatting commands
- generated files to avoid editing
- how to use Graphify in that repo
- safety rules for commits, secrets, and destructive commands

## What Subagents Are

Subagents are useful when a user explicitly asks for parallel agent work. They are best for bounded tasks with clear outputs, for example:

- independent documentation review
- separate frontend/backend implementation slices
- test failure triage while the main agent keeps editing
- security or migration review

Do not use subagents just because a task is important. Use them when parallel work reduces waiting or improves independent review quality.

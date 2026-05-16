# Codex CLI Guide

Use the Codex CLI for local repository work where command execution and file edits matter.

## Good CLI Tasks

- implement a scoped feature
- fix tests
- review a diff
- update docs
- run local commands
- inspect repository structure
- commit and push when explicitly requested

## Start a Session

```bash
cd /path/to/project
codex
```

Then give Codex the goal, constraints, and verification expectations:

```text
Implement the README cleanup described below.
Use Graphify first if graphify-out exists.
Use RTK for noisy commands.
Do not edit generated files.
Run markdown checks if available.
Commit and push after verification.
```

## Key Habits

Use specific outcomes:

```text
Rewrite docs/quickstart.md so a first-time user can install, activate a repo, build a graph, and roll back.
Do not change scripts.
```

Name risky constraints:

```text
Do not include secrets, private paths, tokens, or machine-specific credentials.
```

Ask for verification:

```text
After editing, run git diff --check and any available docs lint command.
```

## Review Mode Prompt

```text
Review this repository change. Prioritize bugs, rollback risks, security issues, broken commands, and missing tests.
List findings first with file and line references.
Do not edit files.
```

## Implementation Prompt

```text
Implement the approved plan.
Before editing, state the files you will change.
After editing, summarize files changed, commands run, and remaining gaps.
```

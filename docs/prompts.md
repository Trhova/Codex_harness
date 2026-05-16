# Prompt Examples

## Use Graphify First

```text
Use Graphify for repo orientation. Read graphify-out/GRAPH_REPORT.md first, then inspect only the files needed for this task.
Use RTK for noisy commands.
```

## Documentation Review With Subagents

```text
Use 5 subagents to review this repo as a practical Codex guide.
Do not edit files yet.

Agent 1: onboarding and README clarity.
Agent 2: installer and rollback safety.
Agent 3: Codex CLI/app workflow guidance.
Agent 4: RTK + Graphify token-usage guidance.
Agent 5: prompt examples and subagent guidance.

Each agent must return top findings, files involved, why it matters, proposed fix, and priority.
After all agents finish, merge duplicates and propose a ranked implementation plan.
```

## Implementation After Review

```text
Implement the approved docs plan.
Do not change installer behavior.
Use placeholders instead of private paths.
Before editing, list files you will change.
After editing, show files changed, commands run, and remaining gaps.
Do not commit or push unless I explicitly ask after reviewing the diff.
```

## Code Review

```text
Review this change. Prioritize bugs, rollback risks, broken commands, and missing tests.
Findings first, ordered by severity, with file and line references.
Do not edit files.
```

## Worker Subagent Implementation

```text
You are one of several agents in this repo. Do not revert edits made by others.
Own only docs/rtk-graphify.md and docs/commands.md.
Improve command accuracy and token-usage guidance.
Return changed files and verification commands.
```

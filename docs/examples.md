# Examples

## Example 1: Prepare a Repo for Codex

Use this when the harness is already installed and you have a real project directory ready.

```bash
/home/<user>/codex_harness/scripts/activate.sh /path/to/project
/home/<user>/codex_harness/scripts/build_graph.sh /path/to/project
cd /path/to/project
codex
```

Prompt:

```text
Read graphify-out/GRAPH_REPORT.md first.
Then explain the repository layout and the safest first documentation improvement.
Do not edit files.
```

Expected result: Codex starts from `graphify-out/GRAPH_REPORT.md`, then verifies important claims by reading specific source or documentation files.

## Example 2: Small Documentation Change

Prompt:

```text
Improve docs/quickstart.md and docs/examples.md so a new contributor understands install, activation, graph refresh, and rollback.
Do not change scripts.
Run git diff --check.
Summarize the diff and checks run before stopping.
```

## Example 3: Parallel Review

Prompt:

```text
Use 4 subagents.
Agent 1 reviews docs for beginners.
Agent 2 reviews installer safety.
Agent 3 reviews rollback completeness.
Agent 4 reviews command examples.
Do not edit files.
Synthesize a ranked plan.
```

Expected result: subagents return findings only. Keep parallel agents read-only until you know which files should change.

## Example 4: Refresh Graph After a Refactor

```bash
/home/<user>/codex_harness/scripts/refresh_graph.sh /path/to/project
cd /path/to/project
rtk git status
```

Use raw logs or direct file reads if RTK's compact output hides details needed to debug a failure.

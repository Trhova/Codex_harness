# Examples

## Example 1: Prepare a Repo for Codex

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

## Example 2: Small Documentation PR

Prompt:

```text
Rewrite README.md and docs/quickstart.md so a new contributor understands install, activation, graph refresh, and rollback.
Do not change scripts.
Run git diff --check.
Commit and push after verification.
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

## Example 4: Refresh Graph After a Refactor

```bash
/home/<user>/codex_harness/scripts/refresh_graph.sh /path/to/project
cd /path/to/project
rtk git status
```

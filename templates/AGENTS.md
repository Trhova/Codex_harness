<!-- codex_harness:project:start -->
This workspace is managed by `codex_harness`.

Command policy:
- Prefer `rtk` for high-volume shell commands when practical.
- Use `rtk git status`, `rtk git diff`, `rtk grep`, `rtk find`, `rtk test pytest`, and similar wrappers before raw commands that would emit large outputs.
- Fall back to raw commands when `rtk` does not support the command or when unfiltered output is required for correctness.

Graph policy:
- This project has a graphify knowledge graph at `graphify-out/`.
- Before answering architecture or codebase questions, read `graphify-out/GRAPH_REPORT.md` for god nodes and community structure.
- If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw files broadly.
- If `graphify-out/GRAPH_REPORT.md` is missing, build or refresh it with `/path/to/codex_harness/scripts/build_graph.sh /path/to/project` before falling back to broad raw file scans.
- Refresh the graph with `/path/to/codex_harness/scripts/refresh_graph.sh /path/to/project` after meaningful codebase changes.
<!-- codex_harness:project:end -->

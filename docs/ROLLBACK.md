# Rollback

> [!NOTE]
> The expanded public rollback guide is now [rollback.md](rollback.md). This file is kept for compatibility with older links and still documents the original rollback model.

The integration is reversible in two layers:

1. `git -C /home/trhova/codex_harness log --stat`
2. `/home/trhova/codex_harness/scripts/uninstall.sh`

`uninstall.sh` restores every bootstrap file and every activated target recorded in `manifests/changes.json`.

Typical rollback flow:

```bash
/home/trhova/codex_harness/scripts/deactivate.sh /path/to/project
/home/trhova/codex_harness/scripts/uninstall.sh
git -C /home/trhova/codex_harness status
```

If you want to inspect what will be restored first, open:

- `manifests/changes.json`
- `state/backups/<timestamp>/`

Bootstrap-managed files outside the harness repo:

- `~/.codex/AGENTS.md`
- `~/.codex/RTK.md`
- `~/.bashrc` RTK PATH block managed by the harness

Target-managed files depend on which projects are activated. For a Codex target, they can include:

- `<project>/AGENTS.md`
- `<project>/.codex/hooks.json`
- `~/.codex/config.toml`

RTK global Codex setup is applied by the official command:

```bash
/home/trhova/codex_harness/bin/rtk init -g --codex
```

The harness backs up `~/.codex/AGENTS.md` and `~/.codex/RTK.md` before running that command, records pre/post file state in `manifests/changes.json`, and restores exact backups during uninstall.
It also adds and removes one harness-managed `~/.bashrc` block that sources the repo-owned RTK PATH export file.

Project activation uses Graphify's official `graphify codex install` command and records each target separately under `manifests/changes.json`.

The intended Codex behavior after bootstrap is to prefer `rtk` for non-trivial shell commands in this workspace. That preference comes from the harness-managed Codex instructions, not from a hard shell interceptor inside Codex.

`deactivate.sh /path/to/project` restores that target's exact backups or removes files that were created only for that target. `uninstall.sh` deactivates all recorded targets, then removes the harness bootstrap state.

Graph output generation is separate from activation:

- `scripts/build_graph.sh /path/to/project` rebuilds the code graph through the harness-managed Graphify Python package.
- `scripts/refresh_graph.sh /path/to/project` runs the same code-only rebuild path, which updates `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json`.

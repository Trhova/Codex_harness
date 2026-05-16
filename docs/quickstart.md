# Quickstart

This page takes you from a fresh clone to a target repo that Codex can inspect with RTK and Graphify guidance.

## Before You Start

You need:

- a Unix-like shell such as Linux, macOS, or WSL2
- `git`, `python3`, `curl`, and `tar`
- network access for Python packages and the RTK release download
- a target project directory that already exists

The installer changes local files under this machine's Codex and shell configuration. It records those changes in `manifests/changes.json` and stores backups under `state/backups/`, but you should still start from a Git-clean harness checkout and avoid running it from a directory that contains private or irreplaceable files.

## 1. Clone the Harness

```bash
git clone <codex-harness-repo-url> /home/<user>/codex_harness
cd /home/<user>/codex_harness
```

## 2. Install

```bash
./scripts/install.sh
```

The installer creates a Python virtual environment, installs Graphify, downloads the RTK binary, updates a managed shell PATH block, runs RTK's Codex setup, and records backups in `manifests/changes.json`.

Expected signs of success:

```bash
test -x bin/rtk
test -x .venv/bin/graphify
cat manifests/changes.json
```

If install stops with `bootstrap already recorded`, this harness already has an active bootstrap record. Inspect `manifests/changes.json`; run `./scripts/uninstall.sh` only if you intend to remove the recorded setup first.

## 3. Restart or Source Your Shell

```bash
source ~/.bashrc
command -v rtk
```

`command -v rtk` should print a path ending in `codex_harness/bin/rtk`. If it does not, open a new shell or check whether your shell reads a different profile file.

## 4. Activate a Target Repository

```bash
./scripts/activate.sh /path/to/project
```

Activation runs Graphify's Codex install flow for that project and records any touched files.

The target path must already exist. Expected target files after activation include:

```text
/path/to/project/AGENTS.md
/path/to/project/.codex/hooks.json
```

Activation can also update `~/.codex/config.toml`. If activation stops with `target already activated`, the target already has a manifest record.

## 5. Build the First Graph

```bash
./scripts/build_graph.sh /path/to/project
```

In the target repo, check:

```bash
ls graphify-out
sed -n '1,120p' graphify-out/GRAPH_REPORT.md
```

Expected generated files include `graphify-out/GRAPH_REPORT.md` and `graphify-out/graph.json`. If the command says the project root does not exist or cannot be opened, check the path and create or clone the project first.

## 6. Use Codex in the Target Repo

Open Codex from the target repository and ask it to start from the graph:

```text
Use Graphify first. Read graphify-out/GRAPH_REPORT.md, then inspect only the files needed for this task.
Use RTK for noisy shell commands.
```

## 7. Refresh the Graph After Larger Changes

```bash
/home/<user>/codex_harness/scripts/refresh_graph.sh /path/to/project
```

Refresh after broad file moves, refactors, or new modules. For tiny documentation-only edits, refreshing is usually optional.

## 8. Roll Back If Needed

Deactivate one project:

```bash
/home/<user>/codex_harness/scripts/deactivate.sh /path/to/project
```

Uninstall all harness-managed changes:

```bash
/home/<user>/codex_harness/scripts/uninstall.sh
```

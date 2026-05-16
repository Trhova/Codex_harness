# Quickstart

This page takes you from a fresh clone to a target repo that Codex can inspect with RTK and Graphify guidance.

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

## 3. Restart or Source Your Shell

```bash
source ~/.bashrc
command -v rtk
```

## 4. Activate a Target Repository

```bash
./scripts/activate.sh /path/to/project
```

Activation runs Graphify's Codex install flow for that project and records any touched files.

## 5. Build the First Graph

```bash
./scripts/build_graph.sh /path/to/project
```

In the target repo, check:

```bash
ls graphify-out
sed -n '1,120p' graphify-out/GRAPH_REPORT.md
```

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

## 8. Roll Back If Needed

Deactivate one project:

```bash
/home/<user>/codex_harness/scripts/deactivate.sh /path/to/project
```

Uninstall all harness-managed changes:

```bash
/home/<user>/codex_harness/scripts/uninstall.sh
```

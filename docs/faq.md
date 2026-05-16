# FAQ

## Is This an Official Codex Project?

No. This is a local harness and guide. Use official Codex documentation as the source of truth for current product behavior.

## Does the Harness Change My Global Codex Files?

Yes. Bootstrap can update files under `~/.codex/` and your shell profile. It records backups and can uninstall those changes.

## Does Activation Change a Target Repo?

Yes. Activation can add or update project-level Codex/Graphify files such as `AGENTS.md` and `.codex/hooks.json`.

## What Should I See After Install?

These checks should pass from the harness repo:

```bash
test -x bin/rtk
test -x .venv/bin/graphify
command -v rtk
cat manifests/changes.json
```

`command -v rtk` may require a new shell or `source ~/.bashrc`.

## What Should I See After Building a Graph?

In the target repo, expect:

```text
graphify-out/GRAPH_REPORT.md
graphify-out/graph.json
```

The report is a starting map, not a source of truth. Ask Codex to verify important conclusions against the actual files.

## Should I Commit `graphify-out/`?

Usually no. Treat it as generated output unless your team explicitly wants to version it. This repo ignores `graphify-out/` because its graph is noisy due to vendored dependencies.

## Should Codex Always Use RTK?

No. RTK is best for non-trivial output. Raw commands are fine for tiny exact output.

## Why Is My Graphify Report Huge?

Generated files, vendored dependencies, and large lockfiles can dominate the graph. Exclude or ignore generated areas where practical, and ask Codex to verify important conclusions against source files.

## Why Did Install or Activation Stop?

Common causes:

- `bootstrap already recorded`: the harness is already installed according to `manifests/changes.json`.
- `target already activated`: that project already has an activation record.
- `bootstrap must be completed`: run `./scripts/install.sh` before `./scripts/activate.sh`.
- `Unsupported platform`: RTK binary detection does not recognize your OS or CPU.
- `project root does not exist or is not a directory`: create or clone the target project before building a graph.

## How Do I Undo Everything?

Run:

```bash
/home/<user>/codex_harness/scripts/uninstall.sh
```

Then inspect:

```bash
cat manifests/changes.json
git status
```

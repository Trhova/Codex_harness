# codex_harness

`codex_harness` is a small helper project for people who use Codex in a chat-style workflow and want lower token usage, better codebase navigation, and an easy rollback path.

It combines two tools:

- `rtk` to reduce noisy command output before it reaches Codex
- `graphify` to build a lightweight knowledge graph of a project so Codex can navigate structure instead of repeatedly searching raw files

The project is designed to be reversible. It keeps track of what it changes, backs up important Codex files before editing them, and provides an uninstall path that restores the previous state.

## What this is for

If you work in VS Code and use Codex in a chat window, you usually do not want to think about shell tooling, hooks, or agent instructions every time you start a project.

This repo gives you a simple setup that:

- makes Codex prefer lower-noise shell commands through `rtk`
- adds graph-based project guidance through `graphify`
- keeps installation and rollback in one place

## What it changes

When installed, the harness can manage:

- reusable tooling inside `codex_harness` itself
- RTK's official Codex integration through `rtk init -g --codex`
- project-level Graphify activation when you explicitly target a project
- project `AGENTS.md`, project `.codex/hooks.json`, and `~/.codex/config.toml` when Graphify activation needs them

The harness records these changes in `manifests/changes.json` and stores backups under `state/backups/`.

Bootstrap is the canonical way to enable the RTK preference in a new workspace. Once the harness is installed, Codex should prefer `rtk` for noisy shell work unless a raw command is needed for correctness or the wrapper does not exist.

Bootstrap also adds the harness-installed `rtk` binary to your shell `PATH` through one managed `~/.bashrc` block, so `rtk` works directly from a new shell after sourcing your profile.

## How to use this with Codex

You do not need to be a programmer to use this.

If you already use VS Code and chat with Codex:

1. Open the folder you want to work in.
2. Open a terminal in VS Code.
3. Run the harness bootstrap script once:

```bash
/home/trhova/codex_harness/scripts/install.sh
```

4. Activate Graphify for a specific project only when you want it:

```bash
/home/trhova/codex_harness/scripts/activate.sh /path/to/project
```

5. Go back to your Codex chat and keep working normally.

After bootstrap, Codex is set up to use the reusable tooling in this repo.

RTK preference is established automatically by the harness bootstrap flow, so you do not need to hand-edit Codex instruction files.

Important: the instruction layers steer Codex, but in practice you still start a chat with a prompt that tells Codex to use RTK and Graphify by default. Example prompt:

```text
For this workspace, use the installed RTK and Graphify setup by default whenever they would improve efficiency or reduce noise.

Behavior rules:

1. **Prefer RTK for noisy shell commands**

   * For commands likely to produce non-trivial output, use `rtk` by default.
   * Typical examples:

     * `rtk git status`
     * `rtk git diff`
     * `rtk rg ...`
     * `rtk find ...`
     * `rtk pytest`
     * `rtk nextflow ...`
   * Only skip RTK when:

     * the output is trivially small,
     * raw unfiltered output is necessary for correctness,
     * or RTK does not support the command.

2. **Prefer Graphify for repo understanding**

   * Before broad file-by-file exploration, check whether Graphify is active for this project and whether graph artifacts exist.
   * If available, use Graphify outputs first, especially:

     * `graphify-out/GRAPH_REPORT.md`
     * `graphify-out/graph.json`
   * Use those artifacts to understand architecture, relationships, and codebase structure before falling back to wide repo scans.

3. **Use Graphify when it would save tokens**

   * For questions like:

     * “explain this repo”
     * “where is X implemented”
     * “how does this system fit together”
     * “what files matter for Y”
   * prefer graph-based understanding before repeated raw search.

4. **Still use normal tools when appropriate**

   * For tiny exact reads or commands where filtering would hurt accuracy, use the raw command.
   * Do not force RTK or Graphify when they add no value.

5. **Be explicit**

   * When you choose RTK or Graphify, briefly note that you are doing so.
   * If you are not using them for a task where they might have applied, briefly state why.

In short:

* use **RTK** for noisy command output
* use **Graphify** for codebase understanding
* fall back to raw commands and raw file inspection only when that is the better choice
```

After project activation, Codex is set up to:

- prefer `rtk`-style lower-noise command usage
- look for `graphify` project context before broad searching

The harness does not activate Graphify for every repo by default. Activation is explicit per project.

If you want to build or refresh the graph manually:

```bash
/home/trhova/codex_harness/scripts/build_graph.sh /path/to/project
/home/trhova/codex_harness/scripts/refresh_graph.sh /path/to/project
```

## How to remove it

If you want to remove Graphify from one project:

```bash
/home/trhova/codex_harness/scripts/deactivate.sh /path/to/project
```

If you want to remove the full harness setup:

```bash
/home/trhova/codex_harness/scripts/uninstall.sh
```

`deactivate.sh` restores the target project's backed-up files. `uninstall.sh` removes all activated targets first, then removes the harness bootstrap state.

## Files in this repo

- `scripts/install.sh` bootstraps the reusable harness setup
- `scripts/activate.sh` activates Graphify for one project
- `scripts/deactivate.sh` removes Graphify from one project
- `scripts/build_graph.sh` runs the initial Graphify build
- `scripts/refresh_graph.sh` runs the Graphify update path
- `scripts/uninstall.sh` rolls it back
- `manifests/changes.json` records bootstrap state and target-specific activation state
- `docs/ROLLBACK.md` explains the rollback model

## Important note

This project does not try to hide what it changes. It is meant to be understandable, inspectable, and safe to reverse.

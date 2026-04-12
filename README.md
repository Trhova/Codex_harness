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

- project-level guidance files such as `AGENTS.md`
- a project `.graphifyignore`
- a project `.codex/hooks.json` entry for graphify reminders
- your Codex config at `~/.codex/config.toml`
- RTK's official Codex integration through `rtk init -g --codex`

The harness records these changes in `manifests/changes.json` and stores backups under `state/backups/`.

## How to use this with Codex

You do not need to be a programmer to use this.

If you already use VS Code and chat with Codex:

1. Open the folder you want to work in.
2. Open a terminal in VS Code.
3. Run the install script from this repo:

```bash
/home/trhova/codex_harness/scripts/install.sh
```

4. Go back to your Codex chat and keep working normally.

After installation, Codex is set up to:

- prefer `rtk`-style lower-noise command usage
- look for `graphify` project context before broad searching

You do not need to manually call these tools every time. The point of the harness is to make that behavior the default.

## How to remove it

If you want to undo the setup:

```bash
/home/trhova/codex_harness/scripts/uninstall.sh
```

That uninstall step restores backed-up files when they existed before and removes files that were created only by the harness.

## Files in this repo

- `scripts/install.sh` installs the harness-managed setup
- `scripts/uninstall.sh` rolls it back
- `scripts/refresh_graph.sh` refreshes the graphify project graph
- `manifests/changes.json` records the current installed state
- `docs/ROLLBACK.md` explains the rollback model

## Important note

This project does not try to hide what it changes. It is meant to be understandable, inspectable, and safe to reverse.

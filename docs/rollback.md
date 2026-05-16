# Rollback Guide

The harness is designed to be reversible. It records managed changes in `manifests/changes.json` and stores backups under `state/backups/`.

## Deactivate One Project

```bash
/home/<user>/codex_harness/scripts/deactivate.sh /path/to/project
```

This restores or removes files recorded for that activated project.

## Uninstall Harness Bootstrap

```bash
/home/<user>/codex_harness/scripts/uninstall.sh
```

This deactivates recorded targets, restores bootstrap-managed files, removes harness-installed local artifacts, and resets the manifest.

## Files Commonly Managed

Bootstrap:

- `~/.codex/AGENTS.md`
- `~/.codex/RTK.md`
- `~/.bashrc`

Target activation:

- `<project>/AGENTS.md`
- `<project>/.codex/hooks.json`
- `~/.codex/config.toml`

## Before Uninstalling

Inspect what the harness knows about:

```bash
cat manifests/changes.json
find state/backups -maxdepth 3 -type f
```

## Important Caveat

Rollback restores the recorded backup. If you manually edit a harness-managed file after activation, uninstall may overwrite those later manual edits. Copy out anything important before uninstalling.

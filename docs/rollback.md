# Rollback Guide

The harness is designed to be reversible. It records managed changes in `manifests/changes.json` and stores backups under `state/backups/`.

Rollback is manifest-based. It can restore files the harness recorded, but it cannot recover unrelated files, untracked work, or manual edits made after the recorded backup unless those edits are saved somewhere else.

## Deactivate One Project

```bash
/home/<user>/codex_harness/scripts/deactivate.sh /path/to/project
```

This restores or removes files recorded for that activated project.

If the project is not recorded, the command prints `No active target recorded for ...` and leaves files alone.

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
rtk find state/backups -maxdepth 3 -type f
```

For tracked project files, check for local edits before uninstalling:

```bash
git -C /path/to/project status --short
```

For a fuller review, inspect the target diff before deactivation:

```bash
cd /path/to/project
rtk git status
rtk git diff
```

Save or commit work you want to keep before rollback touches managed files.

## After Rolling Back

Check that the manifest no longer lists the removed target or bootstrap:

```bash
cat /home/<user>/codex_harness/manifests/changes.json
```

For a full uninstall, `bootstrap` should be `null` and `targets` should be empty.

## Important Caveat

Rollback restores the recorded backup. If you manually edit a harness-managed file after activation, uninstall may overwrite those later manual edits. Save, commit, or stash anything important before uninstalling.

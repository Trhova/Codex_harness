# FAQ

## Is This an Official Codex Project?

No. This is a local harness and guide. Use official Codex documentation as the source of truth for current product behavior.

## Does the Harness Change My Global Codex Files?

Yes. Bootstrap can update files under `~/.codex/` and your shell profile. It records backups and can uninstall those changes.

## Does Activation Change a Target Repo?

Yes. Activation can add or update project-level Codex/Graphify files such as `AGENTS.md` and `.codex/hooks.json`.

## Should I Commit `graphify-out/`?

Usually no. Treat it as generated output unless your team explicitly wants to version it. This repo ignores `graphify-out/` because its graph is noisy due to vendored dependencies.

## Should Codex Always Use RTK?

No. RTK is best for non-trivial output. Raw commands are fine for tiny exact output.

## Why Is My Graphify Report Huge?

Generated files, vendored dependencies, and large lockfiles can dominate the graph. Exclude or ignore generated areas where practical, and ask Codex to verify important conclusions against source files.

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

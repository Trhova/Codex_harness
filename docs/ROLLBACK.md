# Rollback

The integration is reversible in two layers:

1. `git -C /home/trhova/codex_harness log --stat`
2. `/home/trhova/codex_harness/scripts/uninstall.sh`

`uninstall.sh` restores every external file recorded in `manifests/changes.json`.

Typical rollback flow:

```bash
/home/trhova/codex_harness/scripts/uninstall.sh
git -C /home/trhova/codex_harness status
```

If you want to inspect what will be restored first, open:

- `manifests/changes.json`
- `state/backups/<timestamp>/`

Files currently managed outside the harness repo:

- `/home/trhova/writer_skill/AGENTS.md`
- `/home/trhova/writer_skill/.graphifyignore`
- `/home/trhova/writer_skill/.codex/hooks.json`
- `/home/trhova/.codex/config.toml`

RTK global Codex setup is applied by the official command:

```bash
/home/trhova/codex_harness/bin/rtk init -g --codex
```

The harness backs up `~/.codex/AGENTS.md` and `~/.codex/RTK.md` before running that command, records pre/post file state in `manifests/changes.json`, and restores exact backups during uninstall.

The uninstall script restores backed-up versions when they existed before installation and deletes files that were created only by the harness.

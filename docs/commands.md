# Commands

Copy and adapt these commands.

## Harness Lifecycle

```bash
cd /home/<user>/codex_harness
./scripts/install.sh
./scripts/activate.sh /path/to/project
./scripts/build_graph.sh /path/to/project
./scripts/refresh_graph.sh /path/to/project
./scripts/deactivate.sh /path/to/project
./scripts/uninstall.sh
```

## Inspect Harness State

```bash
cat manifests/changes.json
find state/backups -maxdepth 3 -type f
```

## RTK

```bash
rtk --help
rtk git status
rtk git diff
rtk grep "pattern"
rtk find . -type f
rtk pytest
```

## Graphify

```bash
graphify .
graphify update .
sed -n '1,160p' graphify-out/GRAPH_REPORT.md
```

## Git Safety

```bash
rtk git status
rtk git diff
git diff --check
git add README.md docs
git commit -m "Improve Codex Harness documentation"
git push
```

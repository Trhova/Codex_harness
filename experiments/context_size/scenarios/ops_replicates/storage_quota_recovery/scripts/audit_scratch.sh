#!/usr/bin/env bash
set -euo pipefail

root="${1:-/scratch/bioinf}"

echo "== filesystem quota =="
lfs quota -h -p bioinf-prod "${root}" || true

echo "== largest project directories =="
du -xh --max-depth=2 "${root}" 2>/dev/null | sort -h | tail -n 20

echo "== checkpoint files newer than 24h =="
find "${root}" -path "*/checkpoints/*" -mtime -1 -type f -printf "%s %p\n" 2>/dev/null |
  sort -n |
  tail -n 20

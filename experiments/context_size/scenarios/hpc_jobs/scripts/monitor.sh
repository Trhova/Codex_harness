#!/usr/bin/env bash
set -euo pipefail

queue="${1:-$USER}"
squeue --user "${queue}" --format="%.18i %.9P %.24j %.8T %.10M %.6D %R"

if compgen -G "logs/*.err" > /dev/null; then
  grep -n "OutOfMemory\\|CANCELLED\\|checkpoint" logs/*.err || true
fi

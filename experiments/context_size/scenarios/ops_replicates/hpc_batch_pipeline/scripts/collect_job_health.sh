#!/usr/bin/env bash
set -euo pipefail

job_filter="${1:-cohort042}"

echo "== queue =="
squeue --name "*${job_filter}*" --format="%.18i %.30j %.8T %.10M %.6D %R" || true

echo "== accounting =="
sacct --name "*${job_filter}*" --format=JobID,JobName%30,State,Elapsed,MaxRSS,ExitCode --parsable2 || true

echo "== log warnings =="
if compgen -G "logs/*.err" > /dev/null; then
  grep -HnE "OutOfMemory|CANCELLED|TIMEOUT|preemption|missing manifest" logs/*.err || true
else
  echo "no stderr logs found"
fi

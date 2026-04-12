#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
PROJECT_ROOT=${PROJECT_ROOT:-/home/trhova/writer_skill}
GRAPHIFY_BIN="${REPO_ROOT}/.venv/bin/graphify"

if [[ ! -x "${GRAPHIFY_BIN}" ]]; then
  echo "graphify is not installed yet: ${GRAPHIFY_BIN}" >&2
  exit 1
fi

cd "${PROJECT_ROOT}"
exec "${GRAPHIFY_BIN}" . --update


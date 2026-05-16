#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
PROJECT_ROOT=${PROJECT_ROOT:-${1:-}}
PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "harness Python environment is not installed yet: ${PYTHON_BIN}" >&2
  exit 1
fi

if [[ -z "${PROJECT_ROOT}" ]]; then
  echo "usage: ${0} /path/to/project" >&2
  exit 1
fi

if [[ ! -d "${PROJECT_ROOT}" ]]; then
  echo "project root does not exist or is not a directory: ${PROJECT_ROOT}" >&2
  exit 1
fi

cd "${PROJECT_ROOT}"
exec "${PYTHON_BIN}" -c "from pathlib import Path; from graphify.watch import _rebuild_code; import sys; sys.exit(0 if _rebuild_code(Path('.')) else 1)"

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
cd "${REPO_ROOT}"

python3 -m json.tool manifests/changes.json >/dev/null
mapfile -t python_files < <(git ls-files '*.py')
if ((${#python_files[@]})); then
  python3 -m py_compile "${python_files[@]}"
fi

mapfile -t shell_files < <(git ls-files '*.sh' 'env/*.sh')
for script in "${shell_files[@]}"; do
  bash -n "${script}"
done

for required in scripts/*.sh env/*.sh; do
  if [[ ! -x "${required}" ]]; then
    echo "expected executable bit on ${required}" >&2
    exit 1
  fi
done

for non_exec in templates/AGENTS.md templates/project.graphifyignore manifests/changes.json; do
  if [[ -x "${non_exec}" ]]; then
    echo "unexpected executable bit on ${non_exec}" >&2
    exit 1
  fi
done

git submodule status --recursive >/dev/null

if git ls-files -z scripts templates manifests env .gitignore .gitmodules | xargs -0 grep -Il $'\r' | grep -q .; then
  echo "CRLF line endings found in tracked harness files" >&2
  exit 1
fi

echo "validation ok"

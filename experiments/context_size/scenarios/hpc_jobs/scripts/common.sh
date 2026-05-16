#!/usr/bin/env bash

load_modules() {
  for module_name in "$@"; do
    module load "${module_name}"
  done
}

prepare_workspace() {
  local run_id="$1"
  mkdir -p "runs/${run_id}" checkpoints logs
  export TMPDIR="runs/${run_id}/tmp"
  mkdir -p "${TMPDIR}"
}

submit_with_dependency() {
  local dependency="$1"
  local script="$2"
  sbatch --dependency="afterok:${dependency}" "${script}"
}

#!/usr/bin/env bash
#SBATCH --job-name=preprocess-array
#SBATCH --array=0-15
#SBATCH --partition=cpu
#SBATCH --mem=8G
#SBATCH --time=01:00:00

set -euo pipefail
source scripts/common.sh

load_modules python/3.11
prepare_workspace "${SLURM_ARRAY_TASK_ID}"
python preprocess.py --shard "${SLURM_ARRAY_TASK_ID}" --shards 16

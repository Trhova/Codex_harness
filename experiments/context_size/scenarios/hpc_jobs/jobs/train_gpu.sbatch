#!/usr/bin/env bash
#SBATCH --job-name=city-train
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=04:00:00

set -euo pipefail
source scripts/common.sh

load_modules cuda/12.2 python/3.11
prepare_workspace "${SLURM_JOB_ID}"
python train.py --checkpoint "checkpoints/${SLURM_JOB_ID}.pt" --epochs 20

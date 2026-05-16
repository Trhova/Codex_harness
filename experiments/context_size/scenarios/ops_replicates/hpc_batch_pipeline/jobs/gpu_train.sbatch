#!/usr/bin/env bash
#SBATCH --job-name=cohort042-train
#SBATCH --partition=gpu
#SBATCH --account=bioinf-prod
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=12
#SBATCH --mem=96G
#SBATCH --time=12:00:00
#SBATCH --signal=B:USR1@120
#SBATCH --output=logs/train_%j.out
#SBATCH --error=logs/train_%j.err

set -euo pipefail

source configs/dataset.env

mkdir -p "${CHECKPOINT_ROOT}" logs

handle_preempt() {
  echo "received preemption signal; writing final checkpoint"
  python scripts/train_model.py --config "${TRAIN_CONFIG}" --checkpoint-dir "${CHECKPOINT_ROOT}" --save-and-exit
}
trap handle_preempt USR1

module purge
module load cuda/12.2 python/3.11

resume_flag=()
if compgen -G "${CHECKPOINT_ROOT}/epoch_*.pt" > /dev/null; then
  latest_checkpoint="$(ls -1 "${CHECKPOINT_ROOT}"/epoch_*.pt | sort | tail -n 1)"
  resume_flag=(--resume "${latest_checkpoint}")
  echo "resuming from ${latest_checkpoint}"
fi

python scripts/train_model.py \
  --config "${TRAIN_CONFIG}" \
  --features "${FEATURE_ROOT}" \
  --checkpoint-dir "${CHECKPOINT_ROOT}" \
  "${resume_flag[@]}"

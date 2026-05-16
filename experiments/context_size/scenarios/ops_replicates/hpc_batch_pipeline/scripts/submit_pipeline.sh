#!/usr/bin/env bash
set -euo pipefail

source configs/dataset.env
mkdir -p logs

preprocess_job="$(sbatch --parsable jobs/preprocess_array.sbatch)"
echo "submitted preprocess array ${preprocess_job}"

train_job="$(sbatch --parsable --dependency="afterok:${preprocess_job}" jobs/gpu_train.sbatch)"
echo "submitted training job ${train_job} afterok:${preprocess_job}"

cat <<STATUS
Pipeline submitted.
  preprocess: ${preprocess_job}
  train:      ${train_job}
  manifest:   ${FASTQ_MANIFEST}
  features:   ${FEATURE_ROOT}
STATUS

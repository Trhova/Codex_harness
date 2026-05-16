#!/usr/bin/env bash
#SBATCH --job-name=cohort042-preprocess
#SBATCH --partition=cpu
#SBATCH --account=bioinf-prod
#SBATCH --array=1-128%24
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --output=logs/preprocess_%A_%a.out
#SBATCH --error=logs/preprocess_%A_%a.err

set -euo pipefail

source configs/dataset.env

sample_id="$(awk -v idx="${SLURM_ARRAY_TASK_ID}" 'NR == idx { print $1 }' "${FASTQ_MANIFEST}")"
fastq_path="$(awk -v idx="${SLURM_ARRAY_TASK_ID}" 'NR == idx { print $2 }' "${FASTQ_MANIFEST}")"

if [[ -z "${sample_id}" || -z "${fastq_path}" ]]; then
  echo "missing manifest row for task ${SLURM_ARRAY_TASK_ID}" >&2
  exit 22
fi

mkdir -p "${FEATURE_ROOT}/${sample_id}"

echo "preprocess sample=${sample_id} fastq=${fastq_path}"
module purge
module load python/3.11 fastp/0.23

python scripts/preprocess_sample.py \
  --sample "${sample_id}" \
  --fastq "${fastq_path}" \
  --output "${FEATURE_ROOT}/${sample_id}" \
  --threads "${PREPROCESS_CPUS}"

echo "complete sample=${sample_id} output=${FEATURE_ROOT}/${sample_id}"

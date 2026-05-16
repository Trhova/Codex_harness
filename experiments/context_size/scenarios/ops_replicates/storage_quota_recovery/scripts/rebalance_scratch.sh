#!/usr/bin/env bash
set -euo pipefail

source_project="${1:-cohort_042}"
scratch_root="${SCRATCH_ROOT:-/scratch/bioinf}"
archive_bucket="${ARCHIVE_BUCKET:-s3://hpc-cold-archive/bioinf}"
source_dir="${scratch_root}/${source_project}"

if [[ ! -d "${source_dir}" ]]; then
  echo "missing source directory ${source_dir}" >&2
  exit 3
fi

echo "archiving cold checkpoints for ${source_project}"
find "${source_dir}/checkpoints" -type f -mtime +14 -name "epoch_*.pt" -print0 |
  while IFS= read -r -d '' checkpoint; do
    relative_path="${checkpoint#"${source_dir}/"}"
    aws s3 mv \
      --only-show-errors \
      --storage-class STANDARD_IA \
      "${checkpoint}" \
      "${archive_bucket}/${source_project}/${relative_path}"
  done

echo "removing temporary feature shards older than 7 days"
find "${source_dir}/features" -type f -mtime +7 -name "*.tmp" -delete

echo "post-cleanup summary"
du -sh "${source_dir}" || true

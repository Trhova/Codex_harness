# Cohort 042 Pipeline Runbook

Submit from the fixture root:

```bash
scripts/submit_pipeline.sh
```

The preprocessing job must finish cleanly before training starts. `submit_pipeline.sh` uses `afterok` so a failed array task blocks the GPU job instead of wasting allocation time.

Common checks:

- Use `scripts/collect_job_health.sh cohort042` when the training job is pending longer than expected.
- Retry a failed preprocessing shard with `sbatch --array=<task_id> jobs/preprocess_array.sbatch`.
- If `train_*.err` contains `received preemption signal`, resubmit `jobs/gpu_train.sbatch`; it resumes from the newest `epoch_*.pt` checkpoint.
- If `preprocess_*.err` contains `missing manifest row`, compare `#SBATCH --array` with the row count in `FASTQ_MANIFEST`.

Escalate to the cluster queue owner when the GPU job is pending on `AssocGrpGRES` for more than four hours.

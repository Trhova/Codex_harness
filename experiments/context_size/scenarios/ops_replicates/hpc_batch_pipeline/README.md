# HPC Batch Pipeline

This fixture models a two-stage Slurm workflow for a genomics team. CPU preprocessing runs as an array job, then GPU training starts only after every shard succeeds.

Key files:

- `jobs/preprocess_array.sbatch` splits FASTQ inputs into per-sample feature shards.
- `jobs/gpu_train.sbatch` trains with checkpoint restart support.
- `scripts/submit_pipeline.sh` submits both stages and wires the `afterok` dependency.
- `scripts/collect_job_health.sh` summarizes `squeue`, `sacct`, and common failure strings.
- `configs/dataset.env` holds dataset paths and resource defaults.
- `docs/runbook.md` describes retry and checkpoint handling.

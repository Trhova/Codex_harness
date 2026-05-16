# Operations Replicates Fixture

This scenario contains compact operations, HPC, and DevOps fixtures for context-size experiments. Each task is built from scripts, configs, docs, and log-style examples so a harness can compare broad repository scanning against targeted retrieval.

Fixtures:

- `hpc_batch_pipeline`: Slurm preprocessing array plus dependent GPU training workflow.
- `ci_deploy_rollout`: GitHub Actions build and Kubernetes deploy workflow with rollout checks.
- `storage_quota_recovery`: Scratch quota incident response for shared HPC storage.

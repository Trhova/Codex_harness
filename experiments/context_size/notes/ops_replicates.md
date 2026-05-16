# Ops Replicates Notes

The `ops_replicates` scenario contains three task-style fixtures for transcript comparison.

Suggested retrieval prompts:

- HPC batch pipeline: find how the preprocessing array is connected to GPU training and how checkpoint preemption is handled.
- CI deploy rollout: find where the deployment image is set, how rollout success is checked, and how a failed readiness probe should be rolled back.
- Storage quota recovery: find why checkpoint jobs failed during the quota incident and which cleanup policy/script remediates it.

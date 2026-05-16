# Operations Notes

Use the GPU partition only for training jobs. CPU preprocessing should run as a Slurm array so failed shards can be retried independently.

Checkpoints are written under `checkpoints/` and logs are written under `logs/`. When a queue is busy, submit preprocessing first and start training with an `afterok` dependency.

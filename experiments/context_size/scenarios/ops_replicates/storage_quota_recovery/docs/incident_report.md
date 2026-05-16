# Scratch Quota Incident Report

Incident date: 2026-05-09

Summary: `bioinf-prod` exceeded the Lustre scratch soft quota after several GPU training jobs wrote dense checkpoints every 10 minutes. New Slurm jobs started failing when checkpoint writes returned `Disk quota exceeded`.

Timeline:

- 08:10: Grafana alert reported 93 percent scratch usage for `bioinf-prod`.
- 08:24: Users reported failed `cohort042-train` jobs with checkpoint write errors.
- 08:39: Operators ran `scripts/audit_scratch.sh /scratch/bioinf` and identified old checkpoint directories.
- 09:15: Cold checkpoints older than 14 days were archived with `scripts/rebalance_scratch.sh cohort_041`.
- 10:05: Scratch usage dropped below the cleanup threshold.

Follow-up actions:

- Change training defaults from `save_every_minutes: 10` to `save_every_minutes: 30`.
- Add a pre-submit check that blocks GPU jobs when project quota exceeds 92 percent.
- Review `configs/quota_policy.yaml` with project owners after each quarterly allocation change.

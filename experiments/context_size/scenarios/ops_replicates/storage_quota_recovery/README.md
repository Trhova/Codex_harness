# Storage Quota Recovery

This fixture models an HPC operations incident where scratch storage exceeds project quota and new jobs fail during checkpoint writes.

Key files:

- `configs/quota_policy.yaml` defines limits, owners, and cleanup thresholds.
- `scripts/audit_scratch.sh` reports heavy directories and recent checkpoint growth.
- `scripts/rebalance_scratch.sh` moves cold artifacts to object storage.
- `docs/incident_report.md` captures the timeline and remediation plan.
- `logs/lustre_quota_2026-05-09.log` and `logs/job_failures_2026-05-09.log` show operator-facing symptoms.

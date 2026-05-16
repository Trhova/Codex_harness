# CI Deploy Rollout

This fixture models a GitHub Actions pipeline that builds an image, publishes it to a registry, deploys it to Kubernetes, and validates the rollout with smoke tests.

Key files:

- `.github/workflows/deploy.yml` defines build, deploy, and smoke-test jobs.
- `scripts/deploy.sh` renders the deployment image and waits for rollout.
- `scripts/smoke_test.sh` checks health and version endpoints.
- `configs/staging.env` and `configs/production.env` set cluster namespace, replica, and host values.
- `docs/deploy_runbook.md` covers rollback and failed rollout triage.
- `logs/` contains example GitHub Actions and Kubernetes output.

# Deploy Runbook

Normal release path:

```bash
scripts/deploy.sh staging registry.internal.example.com/search-api:<sha>
scripts/smoke_test.sh staging
```

Production deploys use the same scripts with `production`. The GitHub Actions workflow sets the image from the commit SHA and passes the environment input to `scripts/deploy.sh`.

Failed rollout triage:

- If `kubectl rollout status` times out, inspect `kubectl -n <namespace> describe pod -l app=search-api`.
- If the smoke test fails on `/version`, confirm the deployment annotation `deploy.image` matches the Actions build output.
- If readiness probes fail after a config-only change, compare `configs/staging.env` and `configs/production.env` before changing the manifest.

Rollback:

```bash
kubectl -n search-prod rollout undo deployment/search-api
kubectl -n search-prod rollout status deployment/search-api --timeout=300s
scripts/smoke_test.sh production
```

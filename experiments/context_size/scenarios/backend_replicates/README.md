# Backend Replicates Fixture

This scenario contains three backend-oriented replicas for context-size experiments.
The fixtures intentionally reuse common backend vocabulary such as `Settings`,
`Repository`, `Cache`, `authorize`, `retry`, `events`, and `pipeline` so broad
searches collect noisy but plausible context.

## Fixtures

- `billing_api`: an invoice-adjustment API with config, auth, cache, routes,
  repository behavior, docs, and tests.
- `warehouse_etl`: a data-processing pipeline with extraction, validation,
  transformations, checkpointing, loading, docs, and tests.
- `session_gateway`: an API gateway/session service with token verification,
  rate limiting, cache invalidation, docs, and tests.

## Suggested Experiment Tasks

1. Billing API: find where duplicate invoice adjustments are rejected and update
   the response shape for the conflict path.
2. Warehouse ETL: find how refund rows affect daily net revenue and add a guard
   for malformed refund amounts.
3. Session Gateway: find how session cache entries are invalidated after token
   rotation and explain the safest place to add observability.

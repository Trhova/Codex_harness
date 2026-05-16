# Backend Replicates Notes

Created for context-size experiments that compare broad baseline scans with
harness-guided search.

Search patterns:

- Billing API: start with `duplicate-adjustment-conflict`, then inspect
  `DuplicateAdjustment`, `create_adjustment`, and `test_duplicate_adjustment_returns_conflict`.
- Warehouse ETL: start with `refund-net-revenue-guard`, then inspect
  `daily_revenue_facts`, `normalize_amount`, and `test_refunds_reduce_net_revenue`.
- Session Gateway: start with `token-rotation-cache-invalidation`, then inspect
  `rotate_signing_key`, `invalidate_key_id`, and `test_rotation_invalidates_sessions_for_old_key`.

# Warehouse Pipeline Notes

Rows are extracted from object storage in arrival order, validated into typed
records, transformed into daily revenue facts, then loaded idempotently.

Refund rows are negative revenue adjustments. The marker
`refund-net-revenue-guard` appears in the transformer and test so a targeted
search can avoid unrelated `amount_cents` handling in other fixtures.

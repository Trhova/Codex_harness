# Warehouse ETL Replica

This fixture models a daily order revenue pipeline. It includes extractor,
validator, transformer, loader, checkpoint, and tests with repeated names that
look like ordinary data-platform code.

Primary task anchor: `refund-net-revenue-guard`.

Search comparison prompt:

> Where are refund rows applied to daily net revenue, and where should malformed
> refund amount handling be added without changing non-refund order rows?

# Billing API Operations

Adjustment requests are accepted only from service clients with the
`billing:adjustments:write` scope. The API stores a dedupe key derived from the
invoice id and adjustment reason.

The conflict response is intentionally documented away from the route handler so
the implementation requires crossing docs, repository, routes, and tests.

Operational marker: `duplicate-adjustment-conflict`.

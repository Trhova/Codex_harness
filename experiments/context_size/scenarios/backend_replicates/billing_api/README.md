# Billing API Replica

This fixture models an internal invoice adjustment API. It has ordinary names
spread across routes, auth, cache, config, and storage to make wide repository
scans less precise.

Primary task anchor: `duplicate-adjustment-conflict`.

Search comparison prompt:

> Where is duplicate invoice adjustment rejection implemented, and what files
> need to change to include the existing adjustment id in the 409 response?

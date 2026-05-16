# Architecture

Requests enter through `Router`, which owns route registration and delegates persistence to `EventStore`. Configuration is isolated in `Settings` so tests can avoid environment mutation.

The database URL is intentionally not opened by this fixture; the storage class is in-memory so the context experiment remains deterministic.

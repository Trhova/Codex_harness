# Session Gateway Replica

This fixture models a gateway that verifies tokens, stores session metadata,
applies rate limits, and invalidates cached sessions after signing-key rotation.

Primary task anchor: `token-rotation-cache-invalidation`.

Search comparison prompt:

> Where does token rotation invalidate cached sessions, and what is the safest
> function to instrument for cache invalidation observability?

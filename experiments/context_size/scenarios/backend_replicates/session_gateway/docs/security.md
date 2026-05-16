# Session Gateway Security Notes

The gateway keeps token verification and cache invalidation separate so token
rotation can be audited without changing request authorization behavior.

The marker `token-rotation-cache-invalidation` identifies the rotation path. The
same files also contain generic cache and auth names to make broad scans noisy.

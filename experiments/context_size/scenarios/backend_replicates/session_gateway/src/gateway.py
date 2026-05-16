from .cache import SessionCache
from .config import GatewaySettings
from .rate_limit import RateLimiter
from .token import TokenVerifier


class SessionGateway:
    def __init__(self, settings: GatewaySettings, verifier: TokenVerifier, cache: SessionCache) -> None:
        self.settings = settings
        self.verifier = verifier
        self.cache = cache
        self.rate_limiter = RateLimiter(settings.rate_limit_per_minute)

    def authenticate(self, request: dict[str, object]) -> dict[str, object]:
        claims = self.verifier.verify(request.get("headers", {}))  # type: ignore[arg-type]
        cached = self.cache.get(claims.subject)
        if cached is not None:
            session = {**cached, "cache": "hit"}
        else:
            session = {"subject": claims.subject, "key_id": claims.key_id, "cache": "miss"}
            self.cache.set(claims.subject, session)
        if not self.rate_limiter.allow(claims.subject):
            return {"status": 429, "error": "rate limit exceeded"}
        return {"status": 200, "session": session}

    def rotate_signing_key(self, new_key_id: str) -> dict[str, object]:
        old_key_id = self.verifier.active_key_id
        self.verifier.rotate_key(new_key_id)
        removed = self.cache.invalidate_key_id(old_key_id)
        # token-rotation-cache-invalidation: this is the observability boundary.
        return {"status": 202, "old_key_id": old_key_id, "new_key_id": new_key_id, "invalidated": removed}

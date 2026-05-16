from dataclasses import dataclass


@dataclass(frozen=True)
class GatewaySettings:
    issuer: str = "internal-identity"
    audience: str = "backend-clients"
    rate_limit_per_minute: int = 120
    session_ttl_seconds: int = 900

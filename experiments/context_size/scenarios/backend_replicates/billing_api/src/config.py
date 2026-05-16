from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    service_name: str = "billing-api"
    issuer: str = "internal-identity"
    adjustment_scope: str = "billing:adjustments:write"
    cache_ttl_seconds: int = 300
    max_adjustment_cents: int = 250_000


def load_settings(env: dict[str, str] | None = None) -> Settings:
    env = env or {}
    return Settings(
        service_name=env.get("SERVICE_NAME", "billing-api"),
        issuer=env.get("TOKEN_ISSUER", "internal-identity"),
        adjustment_scope=env.get("ADJUSTMENT_SCOPE", "billing:adjustments:write"),
        cache_ttl_seconds=int(env.get("CACHE_TTL_SECONDS", "300")),
        max_adjustment_cents=int(env.get("MAX_ADJUSTMENT_CENTS", "250000")),
    )

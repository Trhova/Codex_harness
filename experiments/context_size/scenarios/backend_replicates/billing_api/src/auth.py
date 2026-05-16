from .config import Settings


class AuthorizationError(Exception):
    pass


def authorize(headers: dict[str, str], settings: Settings) -> dict[str, object]:
    token = headers.get("authorization", "").removeprefix("Bearer ").strip()
    scopes = set(headers.get("x-service-scopes", "").split())
    issuer = headers.get("x-token-issuer", "")
    if not token or issuer != settings.issuer:
        raise AuthorizationError("missing or invalid service token")
    if settings.adjustment_scope not in scopes:
        raise AuthorizationError("missing billing adjustment scope")
    return {"subject": headers.get("x-service-subject", "unknown"), "scopes": scopes}

from session_gateway.src.cache import SessionCache
from session_gateway.src.config import GatewaySettings
from session_gateway.src.gateway import SessionGateway
from session_gateway.src.token import TokenVerifier


def headers(key_id: str) -> dict[str, str]:
    return {
        "x-token-issuer": "internal-identity",
        "x-token-audience": "backend-clients",
        "x-token-key-id": key_id,
        "x-subject": "worker-a",
    }


def test_rotation_invalidates_sessions_for_old_key() -> None:
    settings = GatewaySettings()
    gateway = SessionGateway(settings, TokenVerifier(settings), SessionCache(settings.session_ttl_seconds))
    assert gateway.authenticate({"headers": headers("kid-001")})["status"] == 200

    result = gateway.rotate_signing_key("kid-002")

    assert result["invalidated"] == 1
    assert gateway.cache.get("worker-a") is None

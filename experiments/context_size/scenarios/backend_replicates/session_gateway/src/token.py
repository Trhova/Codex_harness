from dataclasses import dataclass

from .config import GatewaySettings


@dataclass(frozen=True)
class TokenClaims:
    subject: str
    issuer: str
    audience: str
    key_id: str


class TokenVerifier:
    def __init__(self, settings: GatewaySettings) -> None:
        self.settings = settings
        self.active_key_id = "kid-001"

    def verify(self, headers: dict[str, str]) -> TokenClaims:
        if headers.get("x-token-issuer") != self.settings.issuer:
            raise PermissionError("invalid issuer")
        if headers.get("x-token-audience") != self.settings.audience:
            raise PermissionError("invalid audience")
        if headers.get("x-token-key-id") != self.active_key_id:
            raise PermissionError("stale signing key")
        return TokenClaims(
            subject=headers.get("x-subject", "anonymous"),
            issuer=self.settings.issuer,
            audience=self.settings.audience,
            key_id=self.active_key_id,
        )

    def rotate_key(self, key_id: str) -> None:
        self.active_key_id = key_id

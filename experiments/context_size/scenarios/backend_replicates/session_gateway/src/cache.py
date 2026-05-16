from time import monotonic


class SessionCache:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, tuple[float, dict[str, object]]] = {}

    def get(self, subject: str) -> dict[str, object] | None:
        expires_at, value = self._sessions.get(subject, (0.0, {}))
        if expires_at < monotonic():
            self._sessions.pop(subject, None)
            return None
        return value

    def set(self, subject: str, session: dict[str, object]) -> None:
        self._sessions[subject] = (monotonic() + self.ttl_seconds, session)

    def invalidate_subject(self, subject: str) -> bool:
        return self._sessions.pop(subject, None) is not None

    def invalidate_key_id(self, key_id: str) -> int:
        removed = 0
        for subject, (_, session) in list(self._sessions.items()):
            if session.get("key_id") == key_id:
                self._sessions.pop(subject, None)
                removed += 1
        return removed

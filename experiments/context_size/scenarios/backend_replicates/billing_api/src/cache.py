from time import monotonic


class Cache:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl_seconds = ttl_seconds
        self._values: dict[str, tuple[float, object]] = {}

    def get(self, key: str) -> object | None:
        expires_at, value = self._values.get(key, (0.0, None))
        if expires_at < monotonic():
            self._values.pop(key, None)
            return None
        return value

    def set(self, key: str, value: object) -> None:
        self._values[key] = (monotonic() + self.ttl_seconds, value)

    def invalidate_invoice(self, invoice_id: str) -> None:
        for key in list(self._values):
            if key.startswith(f"invoice:{invoice_id}:"):
                self._values.pop(key, None)

from collections import defaultdict


class RateLimiter:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self._counts: dict[str, int] = defaultdict(int)

    def allow(self, subject: str) -> bool:
        self._counts[subject] += 1
        return self._counts[subject] <= self.limit

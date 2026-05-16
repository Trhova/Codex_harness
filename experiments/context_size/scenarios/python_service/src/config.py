import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    cache_ttl_seconds: int
    max_page_size: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.getenv("DATABASE_URL", "sqlite:///events.db"),
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "30")),
            max_page_size=int(os.getenv("MAX_PAGE_SIZE", "100")),
        )

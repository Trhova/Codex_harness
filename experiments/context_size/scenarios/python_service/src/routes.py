from .config import Settings
from .storage import EventStore


class Router:
    def __init__(self, settings: Settings, store: EventStore) -> None:
        self.settings = settings
        self.store = store
        self.routes: dict[tuple[str, str], object] = {}

    def add_route(self, method: str, path: str, handler: object) -> None:
        self.routes[(method, path)] = handler

    def health(self, request: dict) -> dict:
        return {"ok": True, "database": self.settings.database_url}

    def create_event(self, request: dict) -> dict:
        payload = request.get("json", {})
        event = self.store.append(payload)
        return {"status": 201, "event": event}

    def list_events(self, request: dict) -> dict:
        requested = int(request.get("query", {}).get("limit", self.settings.max_page_size))
        limit = min(requested, self.settings.max_page_size)
        return {"events": self.store.list_recent(limit)}

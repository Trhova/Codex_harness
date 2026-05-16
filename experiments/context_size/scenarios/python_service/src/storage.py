from datetime import datetime, timezone


class EventStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.events: list[dict] = []

    def append(self, payload: dict) -> dict:
        event = {
            "id": len(self.events) + 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        self.events.append(event)
        return event

    def list_recent(self, limit: int) -> list[dict]:
        return list(reversed(self.events[-limit:]))

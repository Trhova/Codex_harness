from .config import Settings
from .routes import Router
from .storage import EventStore


def create_app(settings: Settings | None = None) -> Router:
    settings = settings or Settings.from_env()
    store = EventStore(settings.database_url)
    router = Router(settings=settings, store=store)
    router.add_route("GET", "/health", router.health)
    router.add_route("POST", "/events", router.create_event)
    router.add_route("GET", "/events", router.list_events)
    return router


def main() -> None:
    app = create_app()
    print(f"service ready with {len(app.routes)} routes")


if __name__ == "__main__":
    main()

from src.app import create_app
from src.config import Settings


def test_health_reports_database() -> None:
    app = create_app(Settings(database_url="sqlite:///:memory:", cache_ttl_seconds=1, max_page_size=2))
    response = app.health({})
    assert response["ok"] is True
    assert response["database"] == "sqlite:///:memory:"


def test_create_and_list_events() -> None:
    app = create_app(Settings(database_url="sqlite:///:memory:", cache_ttl_seconds=1, max_page_size=2))
    app.create_event({"json": {"name": "first"}})
    app.create_event({"json": {"name": "second"}})
    response = app.list_events({"query": {"limit": "5"}})
    assert len(response["events"]) == 2
    assert response["events"][0]["payload"]["name"] == "second"

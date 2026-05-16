from billing_api.src.cache import Cache
from billing_api.src.config import Settings
from billing_api.src.repository import AdjustmentRepository
from billing_api.src.routes import BillingRoutes


def request(payload: dict[str, object]) -> dict[str, object]:
    return {
        "headers": {
            "authorization": "Bearer service-token",
            "x-token-issuer": "internal-identity",
            "x-service-scopes": "billing:adjustments:write metrics:emit",
            "x-service-subject": "settlements-worker",
        },
        "json": payload,
    }


def test_duplicate_adjustment_returns_conflict() -> None:
    routes = BillingRoutes(Settings(), AdjustmentRepository(), Cache(60))
    first = routes.create_adjustment(request({"invoice_id": "inv-101", "reason": "tax", "amount_cents": -1200}))
    second = routes.create_adjustment(request({"invoice_id": "inv-101", "reason": "TAX", "amount_cents": -1200}))

    assert first["status"] == 201
    assert second == {"status": 409, "error": "duplicate-adjustment-conflict"}

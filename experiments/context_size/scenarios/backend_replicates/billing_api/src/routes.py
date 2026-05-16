from .auth import AuthorizationError, authorize
from .cache import Cache
from .config import Settings
from .repository import Adjustment, AdjustmentRepository, DuplicateAdjustment


def serialize_adjustment(adjustment: Adjustment) -> dict[str, object]:
    return {
        "id": adjustment.id,
        "invoice_id": adjustment.invoice_id,
        "reason": adjustment.reason,
        "amount_cents": adjustment.amount_cents,
        "created_by": adjustment.created_by,
    }


class BillingRoutes:
    def __init__(self, settings: Settings, repository: AdjustmentRepository, cache: Cache) -> None:
        self.settings = settings
        self.repository = repository
        self.cache = cache

    def create_adjustment(self, request: dict[str, object]) -> dict[str, object]:
        try:
            principal = authorize(request.get("headers", {}), self.settings)  # type: ignore[arg-type]
        except AuthorizationError as exc:
            return {"status": 403, "error": str(exc)}

        payload = request.get("json", {})  # type: ignore[assignment]
        amount_cents = int(payload.get("amount_cents", 0))
        if abs(amount_cents) > self.settings.max_adjustment_cents:
            return {"status": 422, "error": "adjustment amount exceeds policy"}

        try:
            adjustment = self.repository.create(
                invoice_id=str(payload["invoice_id"]),
                reason=str(payload["reason"]),
                amount_cents=amount_cents,
                created_by=str(principal["subject"]),
            )
        except DuplicateAdjustment as exc:
            # duplicate-adjustment-conflict lives here, but its existing id is only on exc.existing.
            return {"status": 409, "error": str(exc)}

        self.cache.invalidate_invoice(adjustment.invoice_id)
        return {"status": 201, "adjustment": serialize_adjustment(adjustment)}

    def list_adjustments(self, request: dict[str, object]) -> dict[str, object]:
        path = request.get("path", {})
        invoice_id = str(path.get("invoice_id", "")) if isinstance(path, dict) else ""
        cache_key = f"invoice:{invoice_id}:adjustments"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return {"status": 200, "adjustments": cached, "cache": "hit"}
        adjustments = [serialize_adjustment(item) for item in self.repository.list_for_invoice(invoice_id)]
        self.cache.set(cache_key, adjustments)
        return {"status": 200, "adjustments": adjustments, "cache": "miss"}

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class Adjustment:
    id: str
    invoice_id: str
    reason: str
    amount_cents: int
    created_by: str


class DuplicateAdjustment(Exception):
    def __init__(self, existing: Adjustment) -> None:
        super().__init__("duplicate-adjustment-conflict")
        self.existing = existing


class AdjustmentRepository:
    def __init__(self) -> None:
        self._by_id: dict[str, Adjustment] = {}
        self._dedupe: dict[tuple[str, str], str] = {}

    def create(self, invoice_id: str, reason: str, amount_cents: int, created_by: str) -> Adjustment:
        dedupe_key = (invoice_id, reason.casefold())
        if dedupe_key in self._dedupe:
            raise DuplicateAdjustment(self._by_id[self._dedupe[dedupe_key]])
        adjustment = Adjustment(str(uuid4()), invoice_id, reason, amount_cents, created_by)
        self._by_id[adjustment.id] = adjustment
        self._dedupe[dedupe_key] = adjustment.id
        return adjustment

    def list_for_invoice(self, invoice_id: str) -> list[Adjustment]:
        return [item for item in self._by_id.values() if item.invoice_id == invoice_id]

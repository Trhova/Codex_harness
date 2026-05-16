REQUIRED_FIELDS = {"order_id", "event_type", "occurred_on", "amount_cents", "currency"}


class ValidationError(Exception):
    pass


def validate_row(row: dict[str, object]) -> dict[str, object]:
    missing = REQUIRED_FIELDS - set(row)
    if missing:
        raise ValidationError(f"missing fields: {sorted(missing)}")
    if row["event_type"] not in {"purchase", "refund", "chargeback"}:
        raise ValidationError("unsupported event_type")
    if row["currency"] != "DKK":
        raise ValidationError("unsupported currency")
    return row

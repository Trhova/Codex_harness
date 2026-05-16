from warehouse_etl.src.transform import daily_revenue_facts


def test_refunds_reduce_net_revenue() -> None:
    rows = [
        {"order_id": "o-1", "event_type": "purchase", "occurred_on": "2026-05-16", "amount_cents": 5000, "currency": "DKK"},
        {"order_id": "o-1", "event_type": "refund", "occurred_on": "2026-05-16", "amount_cents": "1200", "currency": "DKK"},
    ]

    facts = daily_revenue_facts(rows)

    assert facts == [
        {
            "date": "2026-05-16",
            "order_count": 1,
            "refund_cents": 1200,
            "net_revenue_cents": 3800,
        }
    ]

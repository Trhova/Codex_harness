from collections import defaultdict


def normalize_amount(row: dict[str, object]) -> int:
    raw = row["amount_cents"]
    if isinstance(raw, str):
        raw = raw.strip()
    return int(raw)


def daily_revenue_facts(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    totals: dict[str, int] = defaultdict(int)
    refunds: dict[str, int] = defaultdict(int)
    orders: dict[str, int] = defaultdict(int)

    for row in rows:
        occurred_on = str(row["occurred_on"])
        amount = normalize_amount(row)
        if row["event_type"] == "refund":
            # refund-net-revenue-guard: refunds reduce net revenue.
            refunds[occurred_on] += abs(amount)
            totals[occurred_on] -= abs(amount)
        elif row["event_type"] == "chargeback":
            totals[occurred_on] -= abs(amount)
        else:
            orders[occurred_on] += 1
            totals[occurred_on] += amount

    return [
        {
            "date": date,
            "order_count": orders[date],
            "refund_cents": refunds[date],
            "net_revenue_cents": totals[date],
        }
        for date in sorted(totals)
    ]

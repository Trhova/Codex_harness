class WarehouseClient:
    def __init__(self) -> None:
        self.loaded: dict[tuple[str, str], dict[str, object]] = {}

    def upsert_fact(self, table: str, fact: dict[str, object]) -> None:
        self.loaded[(table, str(fact["date"]))] = fact


def load_daily_facts(client: WarehouseClient, table: str, facts: list[dict[str, object]]) -> int:
    for fact in facts:
        client.upsert_fact(table, fact)
    return len(facts)

class ObjectStore:
    def __init__(self, objects: dict[str, list[dict[str, object]]]) -> None:
        self.objects = objects

    def read_json_rows(self, bucket: str, prefix: str) -> list[dict[str, object]]:
        return list(self.objects.get(f"{bucket}/{prefix}", []))


def extract_order_rows(store: ObjectStore, bucket: str, date_key: str) -> list[dict[str, object]]:
    return store.read_json_rows(bucket, f"orders/date={date_key}")

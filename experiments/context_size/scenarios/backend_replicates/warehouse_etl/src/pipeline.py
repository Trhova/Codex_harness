from .checkpoint import Checkpoint, CheckpointStore
from .config import PipelineConfig
from .extract import ObjectStore, extract_order_rows
from .load import WarehouseClient, load_daily_facts
from .transform import daily_revenue_facts
from .validate import validate_row


class DailyRevenuePipeline:
    def __init__(
        self,
        config: PipelineConfig,
        object_store: ObjectStore,
        warehouse: WarehouseClient,
        checkpoints: CheckpointStore,
    ) -> None:
        self.config = config
        self.object_store = object_store
        self.warehouse = warehouse
        self.checkpoints = checkpoints

    def run(self, date_key: str) -> dict[str, object]:
        raw_rows = extract_order_rows(self.object_store, self.config.source_bucket, date_key)
        valid_rows = [validate_row(row) for row in raw_rows]
        facts = daily_revenue_facts(valid_rows)
        loaded = load_daily_facts(self.warehouse, self.config.destination_table, facts)
        self.checkpoints.save(Checkpoint(date_key=date_key, loaded_rows=loaded, status="loaded"))
        return {"date_key": date_key, "loaded": loaded, "facts": facts}

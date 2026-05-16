from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineConfig:
    source_bucket: str = "orders-raw"
    destination_table: str = "warehouse.daily_revenue"
    checkpoint_key: str = "daily-revenue/checkpoint.json"
    batch_size: int = 500
    strict_refunds: bool = True

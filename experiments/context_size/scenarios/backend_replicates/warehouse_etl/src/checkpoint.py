from dataclasses import dataclass


@dataclass
class Checkpoint:
    date_key: str
    loaded_rows: int
    status: str


class CheckpointStore:
    def __init__(self) -> None:
        self._latest: Checkpoint | None = None

    def save(self, checkpoint: Checkpoint) -> None:
        self._latest = checkpoint

    def latest(self) -> Checkpoint | None:
        return self._latest

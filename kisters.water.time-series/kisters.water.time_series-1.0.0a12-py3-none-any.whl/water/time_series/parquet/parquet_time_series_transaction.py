from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from kisters.water.time_series.memory.memory_time_series_transaction import MemoryTimeSeriesTransaction
from kisters.water.time_series.parquet.parquet_time_series import (
    ParquetTimeSeriesColumnT,
    ParquetTimeSeriesT,
)

if TYPE_CHECKING:
    from kisters.water.time_series.parquet.parquet_store import ParquetStoreT
else:
    ParquetStoreT = TypeVar("ParquetStoreT")


class ParquetTimeSeriesTransaction(
    MemoryTimeSeriesTransaction[ParquetStoreT, ParquetTimeSeriesT, ParquetTimeSeriesColumnT]
):
    def commit(self) -> None:
        super().commit()

        # Sync to parquet file
        if self.modifies_data or self.modifies_metadata:
            self.store._save_table()

from __future__ import annotations

import asyncio
import copy
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Dict, Generic, Iterator, Optional, TypeVar

from kisters.water.time_series.core.exceptions import TimeSeriesTransactionException

if TYPE_CHECKING:
    from kisters.water.time_series.core.time_series import TimeSeriesT
else:
    TimeSeriesT = TypeVar("TimeSeriesT")


class TimeSeriesMetadata(MutableMapping, Generic[TimeSeriesT]):
    """
    This class implements MutableMapping to provide metadata access for TimeSeries.
    """

    name_key = "name"
    short_name_key = "short_name"

    def __init__(self, ts: TimeSeriesT, metadata: Optional[Dict] = None):
        self._metadata = metadata if metadata is not None else {}
        self._ts = ts
        self._original_values = None
        self._transaction = None

    def __getitem__(self, key: str) -> Any:
        return self._metadata[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)

    def __setitem__(self, key: str, value: Any) -> None:
        self._start_transaction_if_needed()
        self._metadata[key] = value
        self._transaction.set_metadata_value(time_series=self._ts, key=key, value=value)

    def __delitem__(self, key: str) -> None:
        self._start_transaction_if_needed()
        del self._metadata[key]
        self._transaction.delete_metadata_value(self._ts, key)

    def __len__(self) -> int:
        return len(self._metadata)

    def __iter__(self) -> Iterator[str]:
        return iter(self._metadata)

    def _start_transaction_if_needed(self) -> None:
        """
        Start a transaction if there is None and make a backup copy of the metadata.

        """
        if self._transaction is None:
            self._transaction = self._ts.store.transaction()
            self._original_values = copy.deepcopy(self._metadata)

    def commit(self) -> None:
        """
        Commit all the metadata changes to the backend. It rolls back the changes
        in case of failure.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.commit_async())

    async def commit_async(self) -> None:
        """
        Commit asynchronously all the metadata changes to the backend.
        It rolls back the changes in case of failure.
        """
        try:
            await self._transaction.commit_async()
        except TimeSeriesTransactionException:
            self._metadata = self._original_values
        finally:
            self._transaction = None
            self._original_values = None

    def refresh(self) -> None:
        """
        Refresh and update the metadata object with the most recent version from the backend.
        """
        with self._ts.store.transaction() as t:
            op = t.read_metadata(self._ts.path)
        self._metadata = op.metadata

    async def refresh_async(self) -> None:
        async with self._ts.store.transaction() as t:
            op = t.read_metadata(self._ts.path)
        self._metadata = op.metadata

    @property
    def name(self) -> str:
        return self._metadata[self.name_key]

    @property
    def short_name(self) -> str:
        return self._metadata[self.short_name_key]

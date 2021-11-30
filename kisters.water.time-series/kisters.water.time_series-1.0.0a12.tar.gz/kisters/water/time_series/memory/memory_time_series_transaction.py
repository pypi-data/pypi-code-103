from __future__ import annotations

import re
from typing import TYPE_CHECKING, TypeVar

import pandas as pd

from kisters.water.time_series.core.time_series import EnsembleMemberInfo, TimeSeriesColumnT
from kisters.water.time_series.core.time_series_transaction import TimeSeriesTransaction
from kisters.water.time_series.memory.memory_time_series import MemoryTimeSeries, MemoryTimeSeriesT

if TYPE_CHECKING:
    from kisters.water.time_series.memory.memory_store import MemoryStoreT
else:
    MemoryStoreT = TypeVar("MemoryStoreT")


class MemoryTimeSeriesTransaction(
    TimeSeriesTransaction[MemoryStoreT, MemoryTimeSeriesT, TimeSeriesColumnT]
):
    @staticmethod
    def _ensemble_member_key(operation: TimeSeriesTransaction.DataOperation) -> EnsembleMemberInfo:
        return EnsembleMemberInfo(
            pd.to_datetime(operation.t0) if operation.t0 else pd.NaT,
            operation.dispatch_info if not EnsembleMemberInfo.is_null_like(operation.dispatch_info) else "",
            operation.member if not EnsembleMemberInfo.is_null_like(operation.member) else "",
        )

    def _commit_ts_create(self, op: TimeSeriesTransaction.MetadataOperation) -> None:
        op.time_series = MemoryTimeSeries(self._store, op.path, op.metadata, {})
        self._store._time_series[op.path] = op.time_series

    def _commit_ts_read(self, op: TimeSeriesTransaction.MetadataOperation) -> None:
        op.time_series = self._store._time_series[op.path]

    def _commit_ts_filter(self, op: TimeSeriesTransaction.FilterOperation) -> None:
        if op.filter is None:
            op.time_series_iterable = list(self.store._time_series.values())
        else:
            exp = re.compile(
                "^"
                + op.filter.replace(".", "\\.").replace("/", "\\/").replace("?", "\\?").replace("*", ".*")
                + "$"
            )
            op.time_series_iterable = [ts for ts in self.store._time_series.values() if exp.match(ts.path)]

    def _commit_metadata_read(self, op: TimeSeriesTransaction.MetadataOperation) -> None:
        op.metadata = self._store._time_series[op.path].metadata

    def _commit_data_read(self, op: TimeSeriesTransaction.DataOperation) -> None:
        ts = op.time_series
        start, end = op.start, op.end
        try:
            ensemble_member_data = ts._data[self._ensemble_member_key(op)]
        except KeyError:
            raise KeyError(
                f"Time series does not contain ensemble member with t0={op.t0}, member={op.member}, dispatch_info={op.dispatch_info}"
            )
        if start is None and end is None:
            op.data_frame = ensemble_member_data
        elif start is None:
            op.data_frame = ensemble_member_data.loc[ensemble_member_data.index <= end]
        elif end is None:
            op.data_frame = ensemble_member_data.loc[ensemble_member_data.index >= start]
        else:
            op.data_frame = ensemble_member_data.loc[
                (ensemble_member_data.index >= start) & (ensemble_member_data.index <= end)
            ]

    def _commit_metadata_set_value(self, op: TimeSeriesTransaction.MetadataOperation) -> None:
        for key, value in op.metadata.items():
            self._store._time_series[op.path].metadata._metadata[key] = value

    def _commit_data_write(self, op: TimeSeriesTransaction.DataOperation) -> None:
        df = op.data_frame
        ts = op.time_series
        start, end = op.start, op.end
        ensemble_member_key = self._ensemble_member_key(op)
        ensemble_member_data = ts._data.get(ensemble_member_key, None)
        try:
            df.index = df.index.tz_localize("utc")
        except TypeError:
            pass
        mask = None
        if start is not None:
            mask = df.index >= start
        if end is not None:
            mask = df.index <= end if mask is None else mask & (df.index <= end)
        if mask is not None:
            df = df.loc[mask]

        if ensemble_member_data is None:
            ensemble_member_data = df
        else:
            ensemble_member_data = pd.concat([ensemble_member_data, df])
            ensemble_member_data = ensemble_member_data.loc[
                ~ensemble_member_data.index.duplicated(keep="last")
            ]
            ensemble_member_data = ensemble_member_data.reindex(ensemble_member_data.index.sort_values())
        ts._data[ensemble_member_key] = ensemble_member_data

    def _commit_metadata_del_value(self, op: TimeSeriesTransaction.MetadataOperation) -> None:
        for key in op.metadata.keys():
            del self._store._time_series[op.path].metadata._metadata[op.key]

    def _commit_ts_delete(self, op: TimeSeriesTransaction.MetadataOperation) -> None:
        del self._store._time_series[op.path]

    def commit(self) -> None:
        # Override commit() to avoid needless creation of event loop
        for op in self._ts_create_ops:
            self._commit_ts_create(op)
        for op in self._ts_read_ops:
            self._commit_ts_read(op)
        for op in self._ts_filter_ops:
            self._commit_filter_op(op)
        for op in self._metadata_read_ops:
            self._commit_metadata_read(op)
        for op in self._data_read_ops:
            self._commit_data_read(op)
        for op in self._metadata_set_value_ops:
            self._commit_metadata_set_value(op)
        for op in self._data_write_ops:
            self._commit_data_write(op)
        for op in self._metadata_del_value_ops:
            self._commit_metadata_del_value(op)
        for op in self._ts_delete_ops:
            self._commit_ts_delete(op)

    async def commit_async(self) -> None:
        self.commit()

import asyncio
import itertools
from typing import Any, Dict, Iterable, List, Mapping

import pandas as pd

from kisters.water.time_series.core.time_series_transaction import TimeSeriesTransaction
from kisters.water.time_series.kiwis.kiwis_time_series import KiWISTimeSeries


class KiWISTimeSeriesTransaction(TimeSeriesTransaction):
    @classmethod
    def _prepare_params(cls, params: Mapping[str, Any]):
        new_params = {}
        for key, value in params.items():
            if type(value) is list:
                new_params[key] = ",".join(map(str, value))
            else:
                new_params[key] = value
        return new_params

    @classmethod
    def _add_metadata_params(cls, params: Dict[str, Any] = None) -> (Mapping[str, Any], List[str]):
        if params is None:
            result_params = {}
        else:
            result_params = params.copy()

        result_params.setdefault("returnfields", {})

        metakeys = result_params["metadata"] if "metadata" in result_params else []
        metadata = list(itertools.chain.from_iterable(map(cls._convert_metadata, metakeys)))

        result_params["returnfields"] = result_params["returnfields"] + metadata
        if "metadata" in result_params:
            del result_params["metadata"]

        return result_params, ",".join(metadata).split(",")

    @classmethod
    def _convert_metadata(cls, s: str) -> List[str]:
        all_lookup_table = {
            "station": [
                "station_no",
                "station_id",
                "station_name",
                "station_latitude",
                "station_longitude",
                "station_carteasting",
                "station_cartnorthing",
                "station_local_x",
                "station_local_y",
                "station_georefsystem",
                "station_longname",
            ],
            "parametertype": ["parametertype_id", "parametertype_name"],
            "stationparameter": [
                "stationparameter_name",
                "stationparameter_no",
                "stationparameter_longname",
            ],
            "site": ["site_no", "site_id", "site_name"],
            "catchment": ["catchment_no", "catchment_id", "catchment_name"],
            "ts": [
                "ts_id",
                "ts_name",
                "ts_shortname",
                "ts_path",
                "ts_type_id",
                "ts_type_name",
                "ts_unitname",
                "ts_unitsymbol",
                "ts_unitname_abs",
                "ts_unitsymbol_abs",
            ],
        }
        if s.endswith(".all"):
            return all_lookup_table[s.split(".")[0]]
        elif "." in s:
            return [s.replace(".", "_")]
        else:
            return ["ts_" + s]

    @classmethod
    def _merge_metadata(cls, ts_list: Iterable[KiWISTimeSeries], metadata: List[str]):
        for ts in ts_list:
            meta_dict = ts.metadata._metadata

            for key in metadata:
                if "_" not in key:
                    continue
                i = key.index("_")
                bd_type = key[0:i]
                bd_key = key[i + 1 :]
                if bd_type == "ts":
                    meta_dict[bd_key] = meta_dict.pop(key)
                else:
                    if bd_type not in meta_dict:
                        meta_dict[bd_type] = {}

                    meta_dict[bd_type][bd_key] = meta_dict.pop(key)

            meta_dict["name"] = meta_dict.pop("ts_name")

    async def _get_time_series_list(
        self,
        ts_filter: str = None,
        id_list: Iterable[int] = None,
        params: Mapping[str, Any] = None,
    ) -> List[KiWISTimeSeries]:
        """Get the time series list and return a list of TimeSeries objects

        Args:
            ts_filter: The ts filter.
            id_list: The id list.
            params: The additional parameters, which are passed to rest api
                    in addition to the parameters defined by the REST API there
                    are the following keys:
                        metadata = comma separated list of additional meta information
                        where the values are "site", "station", "parameter".

        Returns:
             The list of TimeSeries objects.

        Examples:
            .. code-block:: python

                kiwis.get_by_filter(ts_filter="FR110031fb-e8e7-4381-a942-372aa8141945/CM0514*")

        """
        if params is None:
            params = {}

        if id_list is not None:
            params["ts_id"] = id_list
        if ts_filter is not None:
            params["ts_path"] = ts_filter

        params.setdefault("returnfields", ["ts_id", "ts_name", "ts_path", "ts_shortname"])
        params["returnfields"].append("coverage")

        params, metakeys = self._add_metadata_params(params)
        params = self._prepare_params(params)
        ts_list = []

        j = await self._store._kiwis.getTimeseriesList_async(**params)
        for ts in j.json():
            ts_list.append(KiWISTimeSeries(self.store, ts))
        self._merge_metadata(ts_list, metakeys)
        return iter(ts_list)

    async def _commit_ts_read(self, op: TimeSeriesTransaction.DataOperation) -> None:
        if op.path:
            time_series_list = await self._get_time_series_list(op.path, params=op.kwargs)
        else:
            time_series_list = await self._get_time_series_list(id_list=[op.kwargs["id"]], params=op.kwargs)
        try:
            op.time_series = next(time_series_list)
        except StopIteration:
            raise KeyError(f"No time series found at path {op.path}")

    async def _commit_ts_filter(self, op: TimeSeriesTransaction.DataOperation) -> None:
        op.time_series_iterable = await self._get_time_series_list(op.filter, params=op.kwargs)

    async def _commit_metadata_read(self, op: TimeSeriesTransaction.DataOperation) -> None:
        raise NotImplementedError

    async def _commit_data_read(self, op: TimeSeriesTransaction.DataOperation) -> None:
        # NOTE: KiWIS ensemble time series behavior is that it (1) returns the latest t0
        # when no query params are are used, or (2) return the t0s between from and to.

        # Prepare query parameters
        params = dict(op.kwargs)
        if op.start is not None:
            params["from"] = op.start.isoformat()
        if op.end is not None:
            params["to"] = op.end.isoformat()
        if op.time_series.path is not None:
            params["ts_path"] = op.time_series.path
        else:
            params["ts_id"] = op.time_series.id
        params = self._prepare_params(params)

        # To get *all* t0s we could just use from=1, to=9999, but this places a heavy
        # burden on the server
        if op.time_series._is_ensemble():
            resp = await self._store._kiwis.getTimeseriesEnsembleValues_async(**params)
            ts_id = op.time_series.id
            json_data = resp.json()
            ens_ts_list = json_data[str(ts_id)]
            for ens_ts in ens_ts_list:
                t0_data = pd.to_datetime(ens_ts["ensembledate"])
                dispatch_info_data = ens_ts["ensembledispatchinfo"]
                if op.t0 != t0_data or op.dispatch_info != dispatch_info_data:
                    continue
                j = ens_ts["timeseries"]
                cols = j["columns"].split(",")
                col_member_ts = 2 * (cols.index(op.member) - 1)
                col_member_data = col_member_ts + 1
                member_ts_data = []
                for row in j["data"]:
                    ts_member = row[col_member_ts]
                    data_member = row[col_member_data]
                    member_ts_data.append([t0_data, dispatch_info_data, op.member, ts_member, data_member])
                op.data_frame = pd.DataFrame(
                    member_ts_data,
                    columns=["t0", "dispatch_info", "member", "timestamp", "value"],
                )
                ts_col = "timestamp"
                op.data_frame[ts_col] = pd.to_datetime(op.data_frame[ts_col], utc=True)
                op.data_frame.set_index(ts_col, inplace=True)
                return
            raise KeyError(
                f"Ensemble trace not found for t0={op.t0}, member={op.member}, dispatch_info={op.dispatch_info}"
            )
        else:
            data = await self._store._kiwis.getTimeseriesValues_async(**params)
            j = data.json()[0]
        c = j["columns"].split(",")
        d = j["data"]
        ts_col = "timestamp"
        c[0] = ts_col
        op.data_frame = pd.DataFrame(d, columns=c)
        op.data_frame[ts_col] = pd.to_datetime(op.data_frame[ts_col], utc=True)
        op.data_frame.set_index(ts_col)
        op.data_frame.index = op.data_frame[ts_col]
        op.data_frame = op.data_frame[c[1:]]

    async def commit_async(self) -> None:
        if self.modifies_data or self.modifies_metadata:
            raise NotImplementedError("Write support not implemented")

        await asyncio.gather(
            *itertools.chain(
                (self._commit_ts_read(op) for op in self._ts_read_ops),
                (self._commit_ts_filter(op) for op in self._ts_filter_ops),
                (self._commit_metadata_read(op) for op in self._metadata_read_ops),
                (self._commit_data_read(op) for op in self._data_read_ops),
            )
        )

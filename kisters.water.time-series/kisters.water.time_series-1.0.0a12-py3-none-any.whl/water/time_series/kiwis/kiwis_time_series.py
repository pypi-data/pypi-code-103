import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

import pandas as pd

from kisters.water.time_series.core.time_series import EnsembleMemberInfo, TimeSeries
from kisters.water.time_series.core.time_series_metadata import TimeSeriesMetadata

if TYPE_CHECKING:
    from kisters.water.time_series.kiwis import KiWISStore


class KiWISTimeSeries(TimeSeries):
    """KiWIS REST specific time series implementation"""

    def __init__(self, store: "KiWISStore", metadata: Dict[str, Any]):
        super().__init__(store)
        self._id = int(metadata.pop("ts_id", None))
        self._path = metadata.pop("ts_path", None)
        metadata[TimeSeriesMetadata.short_name_key] = metadata.pop("ts_shortname", None)
        self._metadata = TimeSeriesMetadata(self, metadata)

    @property
    def id(self) -> int:
        return self._id

    @property
    def path(self) -> str:
        return self._path

    @property
    def metadata(self) -> TimeSeriesMetadata:
        return self._metadata

    def _is_ensemble(self) -> bool:
        # I have no better solution...
        # TODO @Alberto do we need this still?
        return "ensemble" in self._metadata.short_name.lower()

    def transform(self, transformation: str) -> TimeSeries:
        if re.match(".*\\(.*\\)", self.path):
            return self.store._get_time_series(path=self.path + ";" + transformation)
        else:
            return self.store._get_time_series(path="tsm(" + self.path + ");" + transformation)

    def get_comments(self, start: datetime = None, end: datetime = None) -> pd.DataFrame:
        """Read comments from a time series and returns it as data frame

        :param start: optional start time stamp
        :param end: optional end time stamp
        """
        return self.read_data_frame(
            start=start,
            end=end,
            returnfields=[
                "Timestamp",
                "Timeseries Comment",
                "Agent Comment",
                "Station Comment",
                "Parameter Comment",
                "Data Comment",
            ],
        )

    def ensemble_members(
        self, t0_start: datetime = None, t0_end: datetime = None
    ) -> List[EnsembleMemberInfo]:
        params = {}
        # NOTE: KiWIS can only return either the latest t0 when no query params are
        # are used, or the t0s between from and to.
        #
        # To get all t0s we could just use from=0001, to=9999, but this places a heavy
        # burden on the server
        #
        # TODO move to transaction, once a more efficient implementation is available.
        if t0_start is not None:
            params["from"] = t0_start.isoformat()
        # else:
        #     params['from'] = '0001'

        if t0_end is not None:
            params["to"] = t0_end.isoformat()
        # else:
        #     params['to'] = '9999'

        if self.path is not None:
            params["ts_path"] = self.path
        else:
            params["ts_id"] = self.id

        data = self.store._kiwis.getTimeseriesEnsembleValues(**params).json()
        ens_ts_list = data[str(self.id)]

        all_ens_members = []

        for ens_ts in ens_ts_list:
            # get t0 and dispatchinfo
            t0 = pd.to_datetime(ens_ts["ensembledate"])
            dispatch_info = ens_ts["ensembledispatchinfo"]
            # members are encoded in the timeseries columns
            ts = ens_ts["timeseries"]
            columns = ts["columns"].lower().split(",")
            if len(columns) < 2 or columns[0] != "timestamp":
                raise ValueError(
                    "Cannot determine the ensemble members for time series "
                    f"{self.id} using this column information: {columns}."
                )
            members = columns[1:]

            ens_members = [
                {"t0": t0, "dispatch_info": dispatch_info, "member": member} for member in members
            ]

            all_ens_members += ens_members
        return all_ens_members

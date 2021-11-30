from kisters.water.time_series.core import TimeSeries, TimeSeriesStore
from kisters.water.time_series.kiwis.kiwis import KiWIS
from kisters.water.time_series.kiwis.kiwis_time_series import KiWISTimeSeries
from kisters.water.time_series.kiwis.kiwis_time_series_transaction import KiWISTimeSeriesTransaction


class KiWISStore(TimeSeriesStore):
    """Connector to KiWIS backend over KiWIS REST API

    Args:
        base_url: Base url of REST API.
        data_source: Optional number identifying the data source.

    Examples:
        .. code-block:: python

            from kisters.water.time_series.kiwis import KiWISStore
            kiwis = KiWISStore('http://kiwis.kisters.de/KiWIS2/KiWIS')
            kiwis.get_by_path('DWD/07367/Precip/CmdTotal.1h')

    """

    def __init__(
        self,
        base_url: str,
        datasource: int = 0,
        user: str = None,
        password: str = None,
        verify_ssl: bool = True,
    ):
        self._kiwis = KiWIS(
            base_url, datasource, user=user, password=password, create_pandas=False, verify_ssl=verify_ssl
        )

    def change_data_source(self, datasource: int = None):
        self._kiwis._KiWIS_data_source = datasource

    def get_by_id(self, id: int, **kwargs) -> TimeSeries:
        with self.transaction() as t:
            op = t.read_time_series(None, id=id, **kwargs)
        return op.time_series

    def transaction(self) -> KiWISTimeSeriesTransaction:
        return KiWISTimeSeriesTransaction(self)

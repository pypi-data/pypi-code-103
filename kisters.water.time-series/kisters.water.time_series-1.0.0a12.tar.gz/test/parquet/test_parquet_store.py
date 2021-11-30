import datetime
import os
import unittest

import numpy as np
import pandas as pd

from kisters.water.time_series.parquet import ParquetStore


class Test(unittest.TestCase):
    def test_io(self):
        filename = "test.pq"
        store = ParquetStore(filename)

        index = pd.date_range("2018-01-01 00:00:00", "2018-01-02 0:00:00", freq="1H", tz="utc")

        ts = store.create_time_series("ts1", "Time Series #1", {})
        df = pd.DataFrame(index=pd.DatetimeIndex(index), data={"value": np.full(len(index), 1)})
        ts.write_data_frame(df)

        ts = store.create_time_series("ts2", "Time Series #2", {})
        df = pd.DataFrame(index=index, data={"value": np.full(len(index), 2)})
        ts.write_data_frame(df)

        ts = store.get_by_path("ts1")
        df = ts.read_data_frame(index[0], index[-1])
        self.assertTrue(np.all(df["value"] == 1))

        ts = store.get_by_path("ts2")
        df = ts.read_data_frame(index[0], index[-1])
        self.assertTrue(np.all(df["value"] == 2))

        del store

        # Ensure the data is still there when re-opening the file
        store = ParquetStore(filename)

        ts = store.get_by_path("ts1")
        df = ts.read_data_frame(index[0], index[-1])
        self.assertTrue(np.all(df["value"] == 1))

        ts = store.get_by_path("ts2")
        df = ts.read_data_frame(index[0], index[-1])
        self.assertTrue(np.all(df["value"] == 2))

        os.remove(filename)

    def test_ensemble_time_series(self):
        filename = "test.pq"
        store = ParquetStore(filename)

        index = pd.date_range("2018-01-01 00:00:00", "2018-01-02 0:00:00", freq="1H", tz="utc")
        t0 = datetime.datetime(2020, 1, 1, 1, 0, 0)

        ts = store.create_time_series("ts1", "Time Series #1", {})
        df = pd.DataFrame(index=index, data={"value": np.full(len(index), 2)})
        ts.write_data_frame(df, t0=t0)

        df = ts.read_data_frame(index[0], index[-1], t0)
        self.assertTrue(np.all(df["value"] == 2))

        del store

        store = ParquetStore(filename)

        ts = store.get_by_path("ts1")
        df = ts.read_data_frame(index[0], index[-1], t0)
        self.assertTrue(np.all(df["value"] == 2))

    def test_empty_time_series(self):
        filename = "test.pq"
        store = ParquetStore(filename)

        index = pd.date_range("2018-01-01 00:00:00", "2018-01-02 0:00:00", freq="1H", tz="utc")

        ts = store.create_time_series("ts1", "Time Series #1", {})
        ts = store.get_by_path("ts1")

        del store

        store = ParquetStore(filename)
        ts = store.get_by_path("ts1")
        df = pd.DataFrame(index=index, data={"value": np.full(len(index), 2)})
        ts.write_data_frame(df)

        df = ts.read_data_frame(index[0], index[-1])
        self.assertTrue(np.all(df["value"] == 2))

        del store

        store = ParquetStore(filename)
        ts = store.get_by_path("ts1")
        df = ts.read_data_frame(index[0], index[-1])
        self.assertTrue(np.all(df["value"] == 2))


if __name__ == "__main__":
    unittest.main()

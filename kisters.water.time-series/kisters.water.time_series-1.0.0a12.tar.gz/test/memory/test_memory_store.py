import unittest

import numpy as np
import pandas as pd

from kisters.water.time_series.memory import MemoryStore


class Test(unittest.TestCase):
    def setUp(self):
        self.store = MemoryStore()

    def test_io(self):
        index = pd.date_range("2018-01-01 00:00:00", "2018-01-02 0:00:00", freq="1H", tz="utc")

        ts = self.store.create_time_series("ts1", "Time Series #1", {})
        df = pd.DataFrame(index=pd.DatetimeIndex(index), data={"value": np.full(len(index), 1)})
        ts.write_data_frame(df)

        ts = self.store.create_time_series("ts2", "Time Series #2", {})
        df = pd.DataFrame(index=index, data={"value": np.full(len(index), 2)})
        ts.write_data_frame(df)

        ts = self.store.get_by_path("ts1")
        df = ts.read_data_frame(index[0], index[-1])
        self.assertTrue(np.all(df["value"] == 1))

        ts = self.store.get_by_path("ts2")
        df = ts.read_data_frame(index[0], index[-1])
        self.assertTrue(np.all(df["value"] == 2))


if __name__ == "__main__":
    unittest.main()

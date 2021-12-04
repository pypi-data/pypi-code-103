import numpy as np
import pandas as pd
import yfinance
from zipline.utils.cli import maybe_show_progress


class yahoo_demo_bundle:
    """
    yahoo_demo_bundle
    """

    def __init__(self, *symbols: str, from_date: str = "2015-01-01", to_date: str = "2019-12-31"):
        """
        asdf

        :param symbols: Symbols that will be ingested and avalible for backtesting in the future
        :param from_date: From which date to collect data from, depends on IPO and yahoo availability
        :param to_date: To which date to collect data. Usally latest point is yesterday
        """
        self.symbols = symbols
        self.from_date = from_date
        self.to_date = to_date

    def get_stock_data(self, symbol: str) -> pd.DataFrame:
        """
        This will get stock data for a symbol between two points.
        returning dataframe containing eod_of_day data

        :param symbol: Symbol of Stock data to return
        """
        stock = yfinance.Ticker(symbol)
        data = stock.history(start=self.from_date, end=self.to_date)
        data.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
                "Dividend": "dividend",
                "Stock Splits": "split",
            },
            inplace=True,
            copy=False,
        )
        return data

    def create_metadata(self) -> pd.DataFrame:
        return pd.DataFrame(
            np.empty(
                len(self.symbols),
                dtype=[
                    ("start_date", "datetime64[ns]"),
                    ("end_date", "datetime64[ns]"),
                    ("auto_close_date", "datetime64[ns]"),
                    ("symbol", "object"),
                    ("exchange", "object"),
                ],
            )
        )

    def writer(self, show_progress: bool) -> iter(int, pd.DataFrame):
        with maybe_show_progress(self.symbols, show_progress, label="Downloading from Yahoo") as it:
            for index, symbol in enumerate(it):
                data = self.get_stock_data(symbol)
                start_date = data.index[0]
                end_date = data.index[-1]
                autoclose_date = end_date + pd.Timedelta(days=1)
                self._df_metadata.iloc[index] = start_date, end_date, autoclose_date, symbol, "NASDAQ"
                yield index, data

    def __call__(
        self,
        environ,
        asset_db_writer,
        minute_bar_writer,
        daily_bar_writer,
        adjustment_writer,
        calendar,
        start_session,
        end_session,
        cache,
        show_progress,
        output_dir,
    ):
        self._df_metadata = self.create_metadata()
        daily_bar_writer.write(self.writer(show_progress), show_progress=show_progress)
        asset_db_writer.write(equities=self._df_metadata)
        adjustment_writer.write()

import pandas as pd
from .exceptions import DataNotFound
import pathlib
from sys import platform


class Helper:
    def __init__(self) -> None:
        self.nse_bse, self.bse_nse = self.fetch_symbols()

    def get_endpoint():
        if platform == "win32":
            return "\stocksymbols.csv"
        else:
            return "/stocksymbols.csv"

    def fetch_symbols(self) -> tuple:
        HERE = pathlib.Path(__file__).parent
        endpoint = self.get_endpoint()
        df = pd.read_csv(str(HERE) + str(endpoint))
        nse_bse = {}
        bse_nse = {}
        for i, row in df.iterrows():
            if pd.isna(row["bse"]) == False:
                nse_bse[row["nse"]] = str(int(row["bse"]))
                bse_nse[str(int(row["bse"]))] = row["nse"]
        return nse_bse, bse_nse

    def bse_to_nse(self, symbol) -> str:
        if self.bse_nse.get(str(symbol)):
            return self.bse_nse[str(symbol)]
        else:
            raise DataNotFound("NSE symbol not found for this BSE symbol")

    def nse_to_bse(self, symbol) -> str:
        if self.nse_bse.get(str(symbol)):
            return self.nse_bse[str(symbol)]
        else:
            raise DataNotFound("BSE symbol not found for this NSE symbol")

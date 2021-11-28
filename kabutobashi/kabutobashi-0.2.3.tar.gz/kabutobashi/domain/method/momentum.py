from dataclasses import dataclass

import pandas as pd

from .method import Method


@dataclass(frozen=True)
class Momentum(Method):
    """
    See Also:
        https://www.sevendata.co.jp/shihyou/technical/momentum.html
    """

    term: int = 25
    method_name: str = "momentum"

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(
            momentum=df["close"].shift(10),
        ).fillna(0)
        df = df.assign(sma_momentum=lambda x: x["momentum"].rolling(self.term).mean())
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.join(self._cross(df["sma_momentum"]))
        df = df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df

    def _color_mapping(self) -> list:
        return [
            {"df_key": "momentum", "color": "", "label": "momentum"},
            {"df_key": "sma_momentum", "color": "", "label": "sma_momentum"},
        ]

    def _visualize_option(self) -> dict:
        return {"position": "lower"}

    def _processed_columns(self) -> list:
        return ["momentum", "sma_momentum"]

    def _parameterize(self, df_x: pd.DataFrame) -> dict:
        return {}

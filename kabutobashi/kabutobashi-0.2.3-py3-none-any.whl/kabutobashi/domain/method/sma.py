from dataclasses import dataclass

import pandas as pd

from .method import Method


@dataclass(frozen=True)
class SMA(Method):
    short_term: int = 5
    medium_term: int = 21
    long_term: int = 70
    method_name: str = "sma"

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(
            sma_short=df["close"].rolling(self.short_term).mean(),
            sma_medium=df["close"].rolling(self.medium_term).mean(),
            sma_long=df["close"].rolling(self.long_term).mean(),
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df["diff"] = df.apply(lambda x: x["sma_long"] - x["sma_short"], axis=1)
        # 正負が交差した点
        df = df.join(self._cross(df["diff"]))
        df = df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df

    def _color_mapping(self) -> list:
        return [
            {"df_key": "sma_long", "color": "#dc143c", "label": f"sma({self.long_term})"},
            {"df_key": "sma_medium", "color": "#ffa500", "label": f"sma({self.medium_term})"},
            {"df_key": "sma_short", "color": "#1e90ff", "label": f"sma({self.short_term})"},
        ]

    def _visualize_option(self) -> dict:
        return {"position": "in"}

    def _processed_columns(self) -> list:
        return ["sma_long", "sma_medium", "sma_short"]

    def _parameterize(self, df_x: pd.DataFrame) -> dict:
        return {}

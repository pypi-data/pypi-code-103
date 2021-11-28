from dataclasses import dataclass

import pandas as pd

from .method import Method


@dataclass(frozen=True)
class BollingerBands(Method):
    """
    株価の勢いの変化や反転の目安、方向を見る`BollingerBands`を計算するクラス。

    See Also:
        * https://www.sevendata.co.jp/shihyou/technical/bori.html
    """

    band_term: int = 12
    continuity_term: int = 10
    method_name: str = "bollinger_bands"

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(mean=df["close"].rolling(self.band_term).mean(), std=df["close"].rolling(self.band_term).std())
        df = df.assign(
            upper_1_sigma=df.apply(lambda x: x["mean"] + x["std"] * 1, axis=1),
            lower_1_sigma=df.apply(lambda x: x["mean"] - x["std"] * 1, axis=1),
            upper_2_sigma=df.apply(lambda x: x["mean"] + x["std"] * 2, axis=1),
            lower_2_sigma=df.apply(lambda x: x["mean"] - x["std"] * 2, axis=1),
            upper_3_sigma=df.apply(lambda x: x["mean"] + x["std"] * 3, axis=1),
            lower_3_sigma=df.apply(lambda x: x["mean"] - x["std"] * 3, axis=1),
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(
            over_upper=df.apply(lambda x: 1 if x["close"] > x["upper_2_sigma"] else 0, axis=1),
            over_lower=df.apply(lambda x: 1 if x["close"] < x["lower_2_sigma"] else 0, axis=1),
            over_upper_continuity=lambda x: x["over_upper"].rolling(self.continuity_term).sum(),
            over_lower_continuity=lambda x: x["over_lower"].rolling(self.continuity_term).sum(),
        )

        df["buy_signal"] = df["over_upper"].apply(lambda x: 1 if x > 0 else 0)
        df["sell_signal"] = df["over_lower"].apply(lambda x: 1 if x > 0 else 0)
        return df

    def _color_mapping(self) -> list:
        return [
            {"df_key": "upper_1_sigma", "color": "#dc143c", "label": "+1s"},
            {"df_key": "lower_1_sigma", "color": "#dc143c", "label": "-1s"},
            {"df_key": "upper_2_sigma", "color": "#ffa500", "label": "+2s"},
            {"df_key": "lower_2_sigma", "color": "#ffa500", "label": "-2s"},
            {"df_key": "upper_3_sigma", "color": "#1e90ff", "label": "+3s"},
            {"df_key": "lower_3_sigma", "color": "#1e90ff", "label": "-3s"},
        ]

    def _visualize_option(self) -> dict:
        return {"position": "in"}

    def _processed_columns(self) -> list:
        return ["upper_2_sigma", "lower_2_sigma", "over_upper_continuity", "over_lower_continuity"]

    def _parameterize(self, df_x: pd.DataFrame) -> dict:
        return {}

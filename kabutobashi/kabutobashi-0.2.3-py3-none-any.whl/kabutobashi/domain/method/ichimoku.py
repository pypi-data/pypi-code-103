from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd

from .method import Method


@dataclass(frozen=True)
class Ichimoku(Method):
    """

    See Also:
        https://kabu.com/investment/guide/technical/04.html
    """

    short_term: int = 12
    medium_term: int = 26
    long_term: int = 52
    method_name: str = "ichimoku"

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(
            # 短期の線
            short_max=lambda x: x["close"].rolling(self.short_term).max(),
            short_min=lambda x: x["close"].rolling(self.short_term).min(),
            # 中期の線
            medium_max=lambda x: x["close"].rolling(self.medium_term).max(),
            medium_min=lambda x: x["close"].rolling(self.medium_term).min(),
            # 長期線
            long_max=lambda x: x["close"].rolling(self.long_term).max(),
            long_min=lambda x: x["close"].rolling(self.long_term).min(),
        )

        # 指標の計算
        df = df.assign(
            line_change=lambda x: (x["short_max"] + x["short_min"]) / 2,
            line_base=lambda x: (x["medium_max"] + x["medium_min"]) / 2,
            # 先行線
            proceeding_span_1=lambda x: (x["line_change"] + x["line_base"]) / 2,
            proceeding_span_2=lambda x: (x["long_max"] + x["long_min"]) / 2,
        )

        # 値のshift
        df = df.assign(
            proceeding_span_1=df["proceeding_span_1"].shift(26),
            proceeding_span_2=df["proceeding_span_2"].shift(26),
            delayed_span=df["close"].shift(26),
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def _color_mapping(self) -> list:
        return [
            {"df_key": "", "color": "", "label": ""},
        ]

    def _visualize_option(self) -> dict:
        return {"position": "in"}

    def _processed_columns(self) -> list:
        return ["line_change", "line_base", "proceeding_span_1", "proceeding_span_2", "delayed_span"]

    def _parameterize(self, df_x: pd.DataFrame) -> dict:
        return {}

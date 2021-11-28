from dataclasses import dataclass

import pandas as pd

from .method import Method


@dataclass(frozen=True)
class MACD(Method):
    """ """

    short_term: int = 12
    long_term: int = 26
    macd_span: int = 9
    method_name: str = "macd"

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        macdを基準として今後上昇するかどうかをスコアで返す。
        値が大きければその傾向が高いことを表している。
        最小値は0で、最大値は無限大である。
        :param df:
        :return:
        """
        # histogramが図として表現されるMACDの値
        df = df.assign(
            # MACDの計算
            ema_short=lambda x: x["close"].ewm(span=self.short_term).mean(),
            ema_long=lambda x: x["close"].ewm(span=self.long_term).mean(),
            macd=lambda x: x["ema_short"] - x["ema_long"],
            signal=lambda x: x["macd"].ewm(span=self.macd_span).mean(),
            # ヒストグラム値
            histogram=lambda x: x["macd"] - x["signal"],
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        # 正負が交差した点
        df = df.join(self._cross(df["histogram"]))
        df = df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df

    def _color_mapping(self) -> list:
        return [
            {"df_key": "macd", "color": "", "label": "macd", "plot": "plot"},
            {"df_key": "signal", "color": "", "label": "signal", "plot": "plot"},
            {"df_key": "histogram", "color": "", "label": "histogram", "plot": "bar"},
        ]

    def _visualize_option(self) -> dict:
        return {"position": "lower"}

    def _processed_columns(self) -> list:
        return ["ema_short", "ema_long", "signal", "macd", "histogram"]

    def _parameterize(self, df_x: pd.DataFrame) -> dict:
        return {}

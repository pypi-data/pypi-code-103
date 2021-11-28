from dataclasses import dataclass

import pandas as pd

from .method import Method


@dataclass(frozen=True)
class Basic(Method):
    """
    株のvolumeやPBR, PSR, PERなどの値を返す。
    parameterizeのみに利用される。
    """

    method_name: str = "basic"

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df_ = df.copy()
        df_["diff"] = -1
        # 正負が交差した点
        df_ = df_.join(self._cross(df_["diff"]))
        df_ = df_.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df_

    def _color_mapping(self) -> list:
        return []

    def _visualize_option(self) -> dict:
        return {"position": "in"}

    def _processed_columns(self) -> list:
        return []

    def _parameterize(self, df_x: pd.DataFrame) -> dict:
        pbr = list(df_x["pbr"])[-1]
        per = list(df_x["per"])[-1]
        psr = list(df_x["psr"])[-1]
        volume = list(df_x["volume"])[-1]
        return {"pbr": pbr, "psr": psr, "per": per, "volume": volume}

from dataclasses import dataclass

import pandas as pd

from .method import Method


@dataclass(frozen=True)
class PsychoLogical(Method):
    """
    See Also:
        https://www.sevendata.co.jp/shihyou/technical/psycho.html
    """

    upper_threshold: float = 0.75
    lower_threshold: float = 0.25
    psycho_term: float = 12
    method_name: str = "psycho_logical"

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        df_ = df.copy()
        df_["shift_close"] = df_["close"].shift(1)
        df_ = df_.fillna(0)
        df_["diff"] = df_.apply(lambda x: x["close"] - x["shift_close"], axis=1)

        df_["is_raise"] = df_["diff"].apply(lambda x: 1 if x > 0 else 0)

        df_["psycho_sum"] = df_["is_raise"].rolling(self.psycho_term).sum()
        df_["psycho_line"] = df_["psycho_sum"].apply(lambda x: x / self.psycho_term)

        df_["bought_too_much"] = df_["psycho_line"].apply(lambda x: 1 if x > self.upper_threshold else 0)
        df_["sold_too_much"] = df_["psycho_line"].apply(lambda x: 1 if x < self.lower_threshold else 0)
        return df_

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df["buy_signal"] = df["sold_too_much"]
        df["sell_signal"] = df["bought_too_much"]
        return df

    def _color_mapping(self) -> list:
        return [
            {"df_key": "psycho_line", "color": "", "label": "psycho_line"},
        ]

    def _visualize_option(self) -> dict:
        return {"position": "lower"}

    def _processed_columns(self) -> list:
        return ["psycho_line", "bought_too_much", "sold_too_much"]

    def _parameterize(self, df_x: pd.DataFrame) -> dict:
        return {}

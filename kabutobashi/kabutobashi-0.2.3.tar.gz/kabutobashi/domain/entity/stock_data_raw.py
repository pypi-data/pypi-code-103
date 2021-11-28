from abc import ABCMeta, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional, Union

import pandas as pd
from cerberus import Validator

from kabutobashi.errors import KabutobashiEntityError

from .stock_data_processed import StockDataProcessed


@dataclass(frozen=True)
class StockDataSingleDay:
    """

    * code: 銘柄コード
    * open: 始値
    * close: 終値
    * high: 高値
    * low: 底値
    * unit: 単位
    * volume: 出来高
    * per: PER
    * psr: PSR
    * pbr: PBR
    * market: 市場
    * dt: その株価の値の日
    * name: 名前
    * industry_type: 業種

    Args:
        code: 銘柄コード
        market: 市場
        industry_type: 業種
        open: 円
        high: 円
        low: 円
        close: 円
    """

    code: str
    market: str
    name: str
    industry_type: str
    open: float
    high: float
    low: float
    close: float
    psr: float
    per: float
    pbr: float
    volume: int
    unit: int
    market_capitalization: str
    issued_shares: str
    dt: str
    _SCHEMA = {
        "code": {"type": "string"},
        "market": {"type": "string"},
        "industry_type": {"type": "string"},
        "name": {"type": "string"},
        "open": {"type": "float"},
        "high": {"type": "float"},
        "low": {"type": "float"},
        "close": {"type": "float"},
        "psr": {"type": "float"},
        "per": {"type": "float"},
        "pbr": {"type": "float"},
        "volume": {"type": "integer"},
        "unit": {"type": "integer"},
        "market_capitalization": {"type": "string"},
        "issued_shares": {"type": "string"},
        "dt": {"type": "string"},
    }

    def __post_init__(self):
        validator = Validator(self._SCHEMA)
        if not validator.validate(self.dumps()):
            raise KabutobashiEntityError(validator)

    @staticmethod
    def schema() -> list:
        return list(StockDataSingleDay._SCHEMA.keys())

    @staticmethod
    def from_page_of(data: dict) -> "StockDataSingleDay":
        label_split = data["stock_label"].split("  ")
        return StockDataSingleDay(
            code=label_split[0],
            market=label_split[1],
            name=data["name"],
            industry_type=data["industry_type"],
            open=float(StockDataSingleDay._convert(data["open"])),
            high=float(StockDataSingleDay._convert(data["high"])),
            low=float(StockDataSingleDay._convert(data["low"])),
            close=float(StockDataSingleDay._convert(data["close"])),
            unit=int(StockDataSingleDay._convert(data["unit"])),
            psr=float(StockDataSingleDay._convert(data["psr"])),
            per=float(StockDataSingleDay._convert(data["per"])),
            pbr=float(StockDataSingleDay._convert(data["pbr"])),
            volume=int(StockDataSingleDay._convert(data["volume"])),
            market_capitalization=data["market_capitalization"],
            issued_shares=data["issued_shares"],
            dt=data["date"],
        )

    @staticmethod
    def _convert(input_value: str) -> str:
        if input_value == "---":
            return "0"
        return input_value.replace("円", "").replace("株", "").replace("倍", "").replace(",", "")

    def dumps(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class StockDataSingleCode:
    """
    単一銘柄の複数日の株データを保持するEntity

    以下のデータを保持する

    * code: 銘柄コード
    * open: 始値
    * close: 終値
    * high: 高値
    * low: 底値
    * unit: 単位
    * volume: 出来高
    * per: PER
    * psr: PSR
    * pbr: PBR
    * market: 市場
    * dt: その株価の値の日
    * name: 名前
    * industry_type: 業種

    Args:
        df: 複数日・単一銘柄を保持するDataFrame
        code: 銘柄コード

    """

    df: pd.DataFrame
    code: str
    REQUIRED_COL = ["code", "open", "close", "high", "low", "unit", "volume", "per", "psr", "pbr", "market", "dt"]
    OPTIONAL_COL = ["name", "industry_type"]

    def __post_init__(self):
        self._null_check()
        self._code_constraint_check(df=self.df)
        if not self._validate():
            raise KabutobashiEntityError(f"required: {self.REQUIRED_COL}, input: {self.df.columns}")

    def _null_check(self):
        if self.df is None:
            raise KabutobashiEntityError("required")

    def _validate(self) -> bool:
        columns = list(self.df.columns)
        # 必須のカラム確認
        if not all([item in columns for item in self.REQUIRED_COL]):
            return False
        return True

    @staticmethod
    def _code_constraint_check(df: pd.DataFrame):
        df_columns = df.columns
        if "code" in df_columns:
            code = list(set(df.code.values))
            if len(code) > 1:
                raise KabutobashiEntityError("multiple code")
            elif len(code) == 0:
                raise KabutobashiEntityError("no code")

    @staticmethod
    def of(df: pd.DataFrame):
        df_columns = df.columns
        # 日付カラムの候補値を探す
        date_column = None
        if "date" in df_columns:
            date_column = "date"
        elif "dt" in df_columns:
            date_column = "dt"
        elif "crawl_datetime" in df_columns:
            date_column = "crawl_datetime"
        if date_column is None:
            raise KabutobashiEntityError("日付のカラム[dt, date, crawl_datetime]のいずれかが存在しません")
        if ("date" in df_columns) and ("dt" in df_columns) and ("crawl_datetime" in df_columns):
            raise KabutobashiEntityError("日付のカラム[dt, date]は片方しか存在できません")

        # 変換
        if date_column == "crawl_datetime":
            df["dt"] = df["crawl_datetime"].apply(lambda x: datetime.fromisoformat(x).strftime("%Y-%m-%d"))
            date_column = "dt"
        # indexにdateを指定
        idx = pd.to_datetime(df[date_column]).sort_index()

        # codeの確認
        StockDataSingleCode._code_constraint_check(df=df)
        if "code" in df_columns:
            code = list(set(df.code.values))[0]
        else:
            code = "-"

        # 数値に変換
        df = df.assign(
            open=df["open"].apply(StockDataSingleCode._replace_comma),
            close=df["close"].apply(StockDataSingleCode._replace_comma),
            high=df["high"].apply(StockDataSingleCode._replace_comma),
            low=df["low"].apply(StockDataSingleCode._replace_comma),
            pbr=df["pbr"].apply(StockDataSingleCode._replace_comma),
            psr=df["psr"].apply(StockDataSingleCode._replace_comma),
            per=df["per"].apply(StockDataSingleCode._replace_comma),
        )

        df.index = idx
        df = df.fillna(0)
        df = df.convert_dtypes()
        return StockDataSingleCode(code=code, df=df)

    @staticmethod
    def _replace_comma(x) -> float:
        """
        pandas内の値がカンマ付きの場合に、カンマを削除する関数
        :param x:
        :return:
        """
        if type(x) is str:
            x = x.replace(",", "")
        try:
            f = float(x)
        except ValueError as e:
            raise KabutobashiEntityError(f"floatに変換できる値ではありません。{e}")
        return f

    def sliding_split(
        self, *, buy_sell_term_days: int = 5, sliding_window: int = 60, step: int = 3
    ) -> (int, pd.DataFrame, pd.DataFrame):
        """
        単一の銘柄に関してwindow幅を`sliding_window`日として、
        保持しているデータの期間の間をslidingしていく関数。

        Args:
            buy_sell_term_days:
            sliding_window:
            step:

        Returns:
            idx: 切り出された番号。
            df_for_x: 特徴量を計算するためのDataFrame。
            df_for_y: `buy_sell_term_days`後のDataFrameを返す。値動きを追うため。

        """
        df_length = len(self.df.index)
        if df_length < buy_sell_term_days + sliding_window:
            raise KabutobashiEntityError("入力されたDataFrameの長さがwindow幅よりも小さいです")
        loop = df_length - (buy_sell_term_days + sliding_window)
        for idx, i in enumerate(range(0, loop, step)):
            offset = i + sliding_window
            end = offset + buy_sell_term_days
            yield idx, self.df[i:offset], self.df[offset:end]

    def get_df(self, minimum=True, latest=False):
        df = self.df

        if latest:
            latest_dt = max(df["dt"])
            df = df[df["dt"] == latest_dt]

        if minimum:
            return df[self.REQUIRED_COL]
        else:
            return df[self.REQUIRED_COL + self.OPTIONAL_COL]

    def to_processed(self, methods: list) -> StockDataProcessed:
        return StockDataProcessed.of(df=self.df, methods=methods)

    def to_parameterize(self, methods: list):
        pass


@dataclass(frozen=True)
class StockDataMultipleCode:
    """
    複数銘柄の複数日の株データを保持するEntity

    単一銘柄のデータのみを返したり、複数銘柄のデータをループで取得できるクラス。

    Args:
        df: 複数日・複数銘柄を保持するDataFrame

    Examples:
        >>> import kabutobashi as kb
        >>> sdmc = kb.example()
        >>> sdsc = sdmc.to_single_code(code=1375)
    """

    df: pd.DataFrame
    REQUIRED_COL = StockDataSingleCode.REQUIRED_COL
    OPTIONAL_COL = StockDataSingleCode.OPTIONAL_COL

    def __post_init__(self):
        self._null_check()
        if not self._validate():
            raise KabutobashiEntityError(f"不正なデータ構造です: {self.df.columns=}")

    def _null_check(self):
        if self.df is None:
            raise KabutobashiEntityError("required")

    def _validate(self) -> bool:
        columns = list(self.df.columns)
        # 必須のカラム確認
        if not all([item in columns for item in self.REQUIRED_COL]):
            return False
        return True

    @staticmethod
    def of(df: pd.DataFrame) -> "StockDataMultipleCode":
        return StockDataMultipleCode(df=df)

    def to_single_code(self, code: Union[str, int]) -> StockDataSingleCode:
        return StockDataSingleCode.of(df=self.df[self.df["code"] == code])

    def to_code_iterable(
        self,
        until: Optional[int] = None,
        *,
        skip_reit: bool = True,
        row_more_than: Optional[int] = 80,
        code_list: list = None,
    ):
        _count = 0
        df = self.df.copy()

        if code_list:
            df = df[df["code"].isin(code_list)]
        if skip_reit:
            df = df[~(df["market"] == "東証REIT")]

        for code, df_ in df.groupby("code"):
            if row_more_than:
                if len(df_.index) < row_more_than:
                    continue
            if until:
                if _count >= until:
                    return
            _count += 1
            yield StockDataSingleCode.of(df=df_)


@dataclass
class IStockDataRepository(metaclass=ABCMeta):
    def read(self, path: Union[str, list]) -> StockDataMultipleCode:
        return self._read(path=path)

    @abstractmethod
    def _read(self, path: Union[str, list]) -> StockDataMultipleCode:
        raise NotImplementedError()

    def save(self, stock_data_multiple_code: StockDataMultipleCode, path: str):
        return self._save(stock_data_multiple_code=stock_data_multiple_code, path=path)

    @abstractmethod
    def _save(self, stock_data_multiple_code: StockDataMultipleCode, path: str):
        raise NotImplementedError()

    @staticmethod
    def _read_csv(path_candidate: Union[str, list], **kwargs) -> Optional[pd.DataFrame]:
        """
        通常のread_csvの関数に加えて、strとlist[str]の場合に縦方向に結合してDataFrameを返す

        Args:
            path_candidate: "path" or ["path_1", "path_2"]

        Returns:
            株のDataFrame
        """
        if type(path_candidate) is str:
            return pd.read_csv(path_candidate, **kwargs)
        elif type(path_candidate) is list:
            if not path_candidate:
                return None
            df_list = [pd.read_csv(p, **kwargs) for p in path_candidate]
            return pd.concat(df_list)
        else:
            return None


@dataclass
class StockDataRepository(IStockDataRepository):
    def _read(self, path: Union[str, list]) -> StockDataMultipleCode:
        df = self._read_csv(path_candidate=path)
        return StockDataMultipleCode.of(df=df)

    def _save(self, stock_data_multiple_code: StockDataMultipleCode, path: str):
        pass

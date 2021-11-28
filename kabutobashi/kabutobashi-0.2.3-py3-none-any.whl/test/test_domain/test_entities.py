import pandas as pd
import pytest

import kabutobashi as kb


class TestStockInfo:
    def test_error_init(self):
        with pytest.raises(kb.errors.KabutobashiEntityError):
            _ = kb.StockDataSingleDay(
                code="1234",
                market="market",
                name="",
                industry_type="industry_type",
                open="",
                high="",
                low="",
                close="",
                psr="",
                per="",
                pbr="",
                volume="",
                unit="",
                market_capitalization="",
                issued_shares="",
                dt="",
            )


class TestStockIpo:
    def test_error_init(self):
        with pytest.raises(kb.errors.KabutobashiEntityError):
            _ = kb.StockIpo(
                code="", market="", manager="", stock_listing_at="", public_offering="", evaluation="", initial_price=""
            )


class TestWeeks52HihLow:
    def test_error_init(self):
        with pytest.raises(kb.errors.KabutobashiEntityError):
            _ = kb.Weeks52HighLow(
                code="", brand_name="", close="", buy_or_sell="", volatility_ratio="", volatility_value=""
            )


class TestStockDataSingleCode:
    def test_of(self, data_path):
        df = pd.read_csv(f"{data_path}/example.csv.gz")
        single_code = df[df["code"] == 1375]
        _ = kb.StockDataSingleCode.of(df=single_code)

        # check None
        with pytest.raises(kb.errors.KabutobashiEntityError):
            _ = kb.StockDataSingleCode(code="-", df=None)

        # check multiple code
        with pytest.raises(kb.errors.KabutobashiEntityError):
            _ = kb.StockDataSingleCode(code="-", df=df)

        # check invalid column
        with pytest.raises(kb.errors.KabutobashiEntityError):
            _ = kb.StockDataSingleCode(code="-", df=single_code[["close"]])

    def test_get_df(self, data_path):
        df = pd.read_csv(f"{data_path}/example.csv.gz")
        single_code = df[df["code"] == 1375]
        sdsc = kb.StockDataSingleCode.of(df=single_code)

        required_cols = kb.StockDataSingleCode.REQUIRED_COL
        optional_cols = kb.StockDataSingleCode.OPTIONAL_COL

        # check minimum df
        minimum_df = sdsc.get_df()
        assert all([(c in minimum_df.columns) for c in required_cols])
        assert all([(c not in minimum_df.columns) for c in optional_cols])

        # check full df
        full_df = sdsc.get_df(minimum=False)
        assert all([(c in full_df.columns) for c in required_cols])
        assert all([(c in full_df.columns) for c in optional_cols])

        latest_date_df = sdsc.get_df(latest=True)
        assert len(latest_date_df.index) == 1


class TestStockDataProcessed:
    def test_of(self):
        sdmc = kb.example()
        sdsc = sdmc.to_single_code(code=1375)
        processed = kb.StockDataProcessed.of(df=sdsc.df, methods=[kb.sma, kb.macd])
        _ = processed.visualize()


class TestStockDataParameterized:
    def test_of(self):
        sdmc = kb.example()
        sdsc = sdmc.to_single_code(code=1375)
        for idx, df_x, df_y in sdsc.sliding_split():
            parameterized = kb.StockDataParameterized.of(df_x=df_x, df_y=df_y, methods=kb.methods)
            assert type(parameterized.x()) is dict
            assert type(float(parameterized.y())) is float
            assert type(parameterized.row()) is dict

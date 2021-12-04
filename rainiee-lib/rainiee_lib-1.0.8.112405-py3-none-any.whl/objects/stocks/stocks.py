from rainiee_lib.dataframe import pandas_df
from rainiee_lib.objects import objects_utils
from rainiee_lib.constants import data_consts
import json
from typing import List
import pandas as pd
class Stock(object):
    def construct(self, json_input):
        self.symbol = json_input['symbol']
        self.symbol_name = json_input['symbol_name']
        self.index = json_input['index']
        self.date = json_input['date']
        self.open_price = json_input['open_price']
        self.high_price = json_input['high_price']
        self.low_price = json_input['low_price']
        self.close_price = json_input['close_price']
        self.pre_close_price = json_input['pre_close_price']
        self.turnover_rate = json_input['turnover_rate']
        self.volume = json_input['volume']
        self.amount = json_input['amount']
        self.total_market_value = json_input['total_market_value']
        self.circulate_market_value = json_input['circulate_market_value']
        self.stock_category = json_input['stock_category']
        self.list_days_index = json_input['list_days_index']
        self.turnover_rate_f = json_input['turnover_rate_f']
        self.volume_ratio = json_input['volume_ratio']
        self.pe = json_input['pe']
        self.pe_ttm = json_input['pe_ttm']
        self.pb = json_input['pb']
        self.ps = json_input['ps']
        self.ps_ttm = json_input['ps_ttm']
        self.dv_ratio = json_input['dv_ratio']
        self.dv_ttm = json_input['dv_ttm']
        self.total_share = json_input['total_share']
        self.float_share = json_input['float_share']
        self.free_share = json_input['free_share']
        self.intra_ret = self.__calc_ret(self.close_price, self.open_price)
        self.inter_ret = self.__calc_ret(self.close_price, self.pre_close_price)
        self.centroid = self.__division(self.high_price + self.low_price, self.pre_close_price) / 2
        self.diff_high = self.__division(self.high_price - self.open_price, self.pre_close_price)
        self.diff_low = self.__division(self.open_price - self.low_price, self.pre_close_price)
        self.volatility = self.__division(self.high_price - self.low_price, self.pre_close_price)

    def __calc_ret(self, end_price, start_price):
        return self.__division(end_price - start_price, start_price)

    def __division(self, numerator, denominator):
        return 0 if denominator == 0 else numerator / denominator

    def to_json(self):
        return self.__dict__

    def from_json(self, json_input):
        self.construct(json_input)
    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))


#由于Stock和StockHistory为固定对接数据中台对象接口，不涉及内部逻辑，所以json_output为[{}]形式
class StockHistory(object):
    def construct(self, stock_history: List[Stock]):
        self.stock_history = stock_history

    def get_symbol(self) -> str:
        return self.stock_history[0].symbol

    def get_stock_history_df(self) -> pd.DataFrame:
        stock_history_df = pandas_df.get_df_obj_list(self.stock_history).set_index("date").sort_index()
        cols = [data_consts.OPEN_PRICE, data_consts.HIGH_PRICE, data_consts.LOW_PRICE, data_consts.CLOSE_PRICE, data_consts.PRE_CLOSE_PRICE,
                data_consts.TURNOVER_RATE, data_consts.VOLUME, data_consts.AMOUNT, data_consts.TOTAL_MKT_VAL, data_consts.CIRC_MKT_VAL]
        stock_history_df[cols] = stock_history_df[cols].apply(pd.to_numeric, errors='coerce', axis=1)
        return stock_history_df
    def get_stock_history_df_range(self, start_index:int, end_index:int) -> pd.DataFrame:
        dataframe = self.get_stock_history_df()
        return dataframe[(dataframe['index'] >= start_index) & (dataframe['index'] <= end_index)]
    def get_stock_history_range(self, start_index:int, end_index:int)  -> pd.DataFrame:
        return self.get_stock_history_df_range(start_index, end_index).reset_index().to_dict("records")
    def to_json(self):
        return objects_utils.to_json_object_list(self.stock_history)
    def from_json(self, json_input):
        self.stock_history = objects_utils.from_json_object_list("Stock", json_input)
    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))



class StockHistoryFetcher(object):
    def construct(self, symbol_list: list, start_index: int, end_index: int):
        self.__assign(symbol_list, start_index, end_index, False)

    def fetcher(self, stock_history_list : List[StockHistory]):
        self.run_mode = True
        self.stock_history_list = stock_history_list
        self.stock_history_map = {x.get_symbol(): x for x in stock_history_list}

    def to_json(self):
        json_output = {"run_mode":self.run_mode,"symbol_list": self.symbol_list, "start_index":self.start_index, "end_index":self.end_index}
        if self.run_mode:
            json_output.update({"stock_history_list":objects_utils.to_json_object_list(self.stock_history_list)})
        return json_output
    def from_json(self, json_input):
        self.__assign(json_input['symbol_list'],json_input['start_index'],json_input['end_index'], json_input['run_mode'])
        if self.run_mode:
            self.stock_history_list = objects_utils.from_json_object_list("StockHistory",json_input['stock_history_list'])
            self.stock_history_map = {x.get_symbol(): x for x in self.stock_history_list}

    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))

    def __assign(self, symbol_list, start_index, end_index, run_mode):
        self.symbol_list = symbol_list
        self.start_index = int(start_index)
        self.end_index = int(end_index)
        self.run_mode = bool(run_mode)




from rainiee_lib.dataframe import pandas_df
from rainiee_lib.objects import objects_utils
from rainiee_lib.constants import data_consts
import json
from typing import List
import pandas as pd
class Index(object):
    def construct(self, json_input):
        self.symbol = json_input['symbol']
        self.symbol_name = json_input['symbol_name']
        self.index = json_input['index']
        self.date = json_input['date']
        self.open_price = float(json_input['open_price'])
        self.high_price = float(json_input['high_price'])
        self.low_price = float(json_input['low_price'])
        self.close_price = float(json_input['close_price'])
        self.pre_close_price = float(json_input['pre_close_price'])
        self.volume = float(json_input['volume'])
        self.amount = float(json_input['amount'])
        self.intra_ret = self.__calc_ret(self.close_price, self.open_price)
        self.inter_ret = self.__calc_ret(self.close_price, self.pre_close_price)
        self.centroid = (self.high_price + self.low_price) / self.pre_close_price / 2
        self.diff_high = (self.high_price - self.open_price) / self.pre_close_price
        self.diff_low = (self.open_price - self.low_price) / self.pre_close_price
        self.volatility = (self.high_price - self.low_price) / self.pre_close_price

    def __calc_ret(self, end_price, start_price):
        if (start_price != 0):
            return (end_price - start_price) / start_price
        else:
            return 0
    def to_json(self):
        return self.__dict__
    def from_json(self, json_input):
        self.construct(json_input)
    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))

class IndexHistory(object):
    def construct(self, index_history: List[Index]):
        self.index_history = index_history

    def get_symbol(self) -> str:
        return self.index_history[0].symbol

    def get_index_history_df(self) -> pd.DataFrame:
        index_history_df = pandas_df.get_df_obj_list(self.index_history).set_index("date").sort_index()
        cols = [data_consts.OPEN_PRICE, data_consts.HIGH_PRICE, data_consts.LOW_PRICE, data_consts.CLOSE_PRICE, data_consts.PRE_CLOSE_PRICE]
        index_history_df[cols] = index_history_df[cols].apply(pd.to_numeric, errors='coerce', axis=1)
        return index_history_df
    def get_index_history_df_range(self, start_index:int, end_index:int) -> pd.DataFrame:
        dataframe = self.get_index_history_df()
        return dataframe[(dataframe['index'] >= start_index) & (dataframe['index'] <= end_index)]
    def get_index_history_range(self, start_index:int, end_index:int)  -> pd.DataFrame:
        return self.get_index_history_df_range(start_index, end_index).reset_index().to_dict("records")
    def to_json(self):
        return objects_utils.to_json_object_list(self.index_history)
    def from_json(self, json_input):
        self.index_history = objects_utils.from_json_object_list("Index", json_input)
    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))



class IndexHistoryFetcher(object):
    def construct(self, symbol_list: list, start_index: int, end_index: int):
        self.__assign(symbol_list, start_index, end_index, False)

    def fetcher(self, index_history_list : List[IndexHistory]):
        self.run_mode = True
        self.index_history_list = index_history_list
        self.index_history_map = {x.get_symbol(): x for x in index_history_list}

    def to_json(self):
        json_output = {"run_mode":self.run_mode,"symbol_list": self.symbol_list, "start_index":self.start_index, "end_index":self.end_index}
        if self.run_mode:
            json_output.update({"index_history_list":objects_utils.to_json_object_list(self.index_history_list)})
        return json_output
    def from_json(self, json_input):
        self.__assign(json_input['symbol_list'],json_input['start_index'],json_input['end_index'], json_input['run_mode'])
        if self.run_mode:
            self.index_history_list = objects_utils.from_json_object_list("IndexHistory",json_input['index_history_list'])
            self.index_history_map = {x.get_symbol(): x for x in self.index_history_list}
    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))

    def __assign(self, symbol_list, start_index, end_index, run_mode):
        self.symbol_list = symbol_list
        self.start_index = int(start_index)
        self.end_index = int(end_index)
        self.run_mode = bool(run_mode)




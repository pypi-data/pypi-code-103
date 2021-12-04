from typing import List
from rainiee_lib.constants import data_consts
from rainiee_lib.objects.stocks import stocks
from rainiee_lib.objects import objects_utils
from rainiee_lib.dataframe import pandas_df
from rainiee_lib.lib import utils
import pandas as pd
import json
class RetPredictions(object):
    def construct(self, stock_history_list : List[stocks.StockHistory],
                  ret_predict_model : str, param = {}):
        self.__assign(stock_history_list, ret_predict_model, param, False)

    def get_returns_df(self):
        returns_df = []
        utils.info('STARTED to enumerate symbol list')
        for stock_history in self.stock_history_list:
            stock_history_df = stock_history.get_stock_history_df()
            symbol = stock_history_df[data_consts.SYMBOL][0]
            stock_history_df[symbol] = stock_history_df['inter_ret']
            hist_df = stock_history_df[[symbol]]
            returns_df = self.__merge_final_df(returns_df, hist_df, symbol)
        utils.info('COMPLETED to enumerate symbol list')
        return returns_df

    def predict(self, mean_returns, cov_matrix):
        self.run_mode = True
        self.mean_returns = mean_returns
        self.cov_matrix = cov_matrix

    def to_json(self):
        json_output = {"run_mode":self.run_mode,
                       "ret_predict_model":self.ret_predict_model,
                       "stock_history_list" :objects_utils.to_json_object_list(self.stock_history_list),
                       "param": self.param}
        if self.run_mode:
            json_output.update({
                "mean_returns":pandas_df.json_write_dataframe(self.mean_returns),
                "cov_matrix":pandas_df.json_write_dataframe(self.cov_matrix)
            })
        return json_output

    def from_json(self, json_input):
        self.__assign(
            objects_utils.from_json_object_list("StockHistory", json_input["stock_history_list"]),
            json_input["ret_predict_model"],
            json_input["param"],
            json_input["run_mode"]
        )
        if self.run_mode:
            self.mean_returns = pandas_df.json_read_dataframe(json_input['mean_returns'])
            self.cov_matrix = pandas_df.json_read_dataframe(json_input['cov_matrix'])

    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))

    def __merge_final_df(self, final_df, hist_df, symbol):
        if len(final_df) == 0:
            final_df = hist_df
        else:
            try:
                final_df = pd.merge(final_df, hist_df, on='date', how='inner')
            except Exception as e:
                utils.info('Excluding symbol [{}] due to exception on join'.format(symbol))
        return final_df

    def __assign(self, stock_history_list : List[stocks.StockHistory],
                 ret_predict_model: str,
                 param : dict,
                 run_mode: bool):
        self.run_mode = run_mode
        self.stock_history_list = stock_history_list
        self.ret_predict_model = ret_predict_model
        self.param = param

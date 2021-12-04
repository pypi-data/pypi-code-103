import json
from typing import List
from rainiee_lib.objects.stocks import stocks
from rainiee_lib.objects import objects_utils
"""
Default:
stock_history_fetcher :: StockHistoryFetcher
funnel_model :: str

Funneled:
funneled_stock_history_list : List[stocks.StockHistory]
exclude_list : List[dict]
"""
class FunnelsRunner(object):
    def construct(self, stock_history_fetcher : stocks.StockHistoryFetcher,
                  funnel_model :str):
        self.__assign(stock_history_fetcher, funnel_model, False)
        self.stock_history_fetcher = stock_history_fetcher
        self.funnel_model = funnel_model

    def run(self, funneled_stock_history_list : List[stocks.StockHistory],
               exclude_list : List[dict]):
        self.run_mode = True
        self.funneled_stock_history_list = funneled_stock_history_list
        self.exclude_list = exclude_list

    def __assign(self, stock_history_fetcher : stocks.StockHistoryFetcher, funnel_model : str, run_mode : bool):
        self.stock_history_fetcher = stock_history_fetcher
        self.funnel_model = funnel_model
        self.run_mode = run_mode

    def to_json(self):
        json_output = {"run_mode":self.run_mode,
                       "funnel_model": self.funnel_model,
                       "stock_history_fetcher":self.stock_history_fetcher.to_json()}
        if self.run_mode:
            json_output.update({"funneled_stock_history_list":objects_utils.to_json_object_list(self.funneled_stock_history_list),
                                "exclude_list":self.exclude_list})
        return json_output
    def from_json(self, json_input):
        self.__assign(objects_utils.from_json_object("StockHistoryFetcher",json_input["stock_history_fetcher"]),
                      json_input["funnel_model"],
                      json_input["run_mode"])
        if(self.run_mode):
            self.funneled_stock_history_list = objects_utils.from_json_object_list("StockHistory", json_input["funneled_stock_history_list"])
            self.exclude_list = json_input["exclude_list"]

    def to_json_str(self):
        return json.dumps(self.to_json())
    def from_json_str(self, json_str):
        self.from_json(json.loads(json_str))


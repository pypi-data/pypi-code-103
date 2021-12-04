import json
from typing import List

from rainiee_lib.constants.data_consts import *
from rainiee_lib.objects import objects_utils
from rainiee_lib.objects.base.base_object import BaseObject
from rainiee_lib.objects.portfolio.portfolio import PortfolioEntries
from rainiee_lib.objects.stocks.indexs import IndexHistoryFetcher
from rainiee_lib.objects.stocks.stocks import Stock, StockHistoryFetcher
import pandas as pd

class PortfolioReturn(BaseObject):

    def construct(self,
                  portfolios:List[PortfolioEntries],
                  items:List[Stock],
                  index:int,
                  daily_p_return:float,
                  daily_p_return_total:float,
                  geometric_mean:float,
                  avg_profit:float,
                  min_hold_profit:float,
                  min_hold_profit_index:int,
                  max_hold_profit:float,
                  max_hold_profit_index:int,
                  benchmark_profit:dict
                  ):
        # 策略组合
        self.portfolios = portfolios
        # 交易日
        self.index = index
        # 策略组合交易日内，个股收益明细
        self.items = items
        # 组合当日收益
        self.daily_p_return = daily_p_return
        # 组合滚动收益
        self.daily_p_return_total = daily_p_return_total
        # 滚动几何平均数
        self.geometric_mean = geometric_mean
        # 算数平均数
        self.avg_profit = avg_profit
        # 滚动最小收益
        self.min_hold_profit = min_hold_profit
        # 滚动最小收益对应的交易日
        self.min_hold_profit_index = min_hold_profit_index
        # 滚动最大收益
        self.max_hold_profit = max_hold_profit
        # 滚动最大收益对应的交易日
        self.max_hold_profit_index = max_hold_profit_index

        # 当天交易日基准收益相关，格式
        '''
        {
          daily_p_return_399300.SZ:1.020001,
          daily_p_return_total_399300.SZ:1.150001
        }
        '''
        objects_utils.set_attrs(self,benchmark_profit)
        return self

    def to_json_str(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def from_json(self,json_data):
        self.__dict__ = json_data


class BacktestResult(BaseObject):

    def construct(self,
                  return_list:List[PortfolioReturn],
                  benchmark_symbol_list:list
                  ):
        last_return = return_list[len(return_list)-1]
        # 回测历史记录
        self.return_list = return_list
        # 回测总收益
        self.p_return_total = objects_utils.get_value(last_return,'daily_p_return_total')
        # 买入日
        self.buy_index = objects_utils.get_value(return_list[0],'index')
        # 持仓天数
        self.hold_day = objects_utils.get_value(last_return,'index') -  self.buy_index + 1

        #回测总收益基准相关，格式
        '''
        {
          p_return_total_399300.SZ:1.150001
        }
        '''
        for benchmark_symbol in benchmark_symbol_list:
            field_name = 'p_return_total_'+benchmark_symbol
            setattr(self,field_name,objects_utils.get_value(last_return,'daily_p_return_total_'+benchmark_symbol))
        return self

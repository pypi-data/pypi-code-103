import uuid
from typing import List

from rainiee_lib.objects import objects_utils
from rainiee_lib.objects.backtesting.backtest_result import BacktestResult
from rainiee_lib.objects.base.base_object import BaseObject


class BacktestStrategyHistory(BaseObject):

    def construct(self,backtest_result:BacktestResult,bt_result_sell_info:{},is_sell):
        # 每次组合的id标识
        self.uuid = 'HIS' + uuid.uuid1().hex
        # 当前组合的回测结果
        self.backtest_result = backtest_result
        # 是否卖出
        self.is_sell = is_sell
        # 给当前组合的每一天绑定信号
        return_list = backtest_result.return_list
        for _return in return_list:
            objects_utils.set_value(_return,'selling_signal_info',bt_result_sell_info.get(objects_utils.get_value(_return,'index')))
        return self



class BacktestStrategyResult(BaseObject):

    def construct(self,
                  backtest_history_list:List[BacktestStrategyHistory],
                  benchmark_symbol_list
                  ):
        # 策略回测历史记录
        self.backtest_history_list = backtest_history_list
        # 策略滚动收益
        self.p_return_roll_total = 1

        # 策略滚动基准收益相关，格式
        '''
        {
          p_return_roll_total_399300.SZ:1.150001
        }
        '''
        self.calculate(benchmark_symbol_list)
        return self


    def calculate(self,benchmark_symbol_list):
        for benchmark_symbol in benchmark_symbol_list:
            setattr(self,'p_return_roll_total_' + benchmark_symbol,1)

        # 计算history滚动收益
        for strategy_history in self.backtest_history_list:
            self.p_return_roll_total = self.p_return_roll_total * strategy_history.backtest_result.p_return_total
            for benchmark_symbol in benchmark_symbol_list:
                benchmark_key = 'p_return_roll_total_' + benchmark_symbol
                setattr(self,benchmark_key,(
                        getattr(self,benchmark_key) * (objects_utils.get_value(strategy_history.backtest_result,'p_return_total_' + benchmark_symbol))
                ))


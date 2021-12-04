from typing import List

from rainiee_lib.objects.backtesting.backtest_result import PortfolioReturn


def daily_return_percentage(stock):
    if stock['pre_close_price'] == 0:
        return 1
    return stock['close_price'] / stock['pre_close_price']

def intraday_return_percentage(stock):
    return stock['close_price'] / stock['open_price']



def compute_geometric_data(data):
    from functools import reduce
    import operator
    gd = reduce(operator.mul, data) ** (1.0 / len(data))
    if type(gd) == complex:
        return gd.real
    return gd
def compute_profit_mean(data):
    sum = 0
    for it in data:
        sum = sum + it
    return sum / len(data)


def compute_mean(return_list:List[PortfolioReturn]):
    index_map = {}
    data = []
    daily_p_return_list=[]
    i = 0
    for ret in return_list:
        daily_p_return_total = round((ret.daily_p_return_total), 5)
        data.append(daily_p_return_total)
        index_map[daily_p_return_total] = ret.index
        daily_p_return_list.append(ret.daily_p_return)
        i = i + 1
    min_hold_profit = min(data)
    min_hold_profit_index = index_map[min_hold_profit]
    max_hold_profit = max(data)
    max_hold_profit_index = index_map[max_hold_profit]
    return round(compute_geometric_data(daily_p_return_list), 5), round(compute_profit_mean(daily_p_return_list),5), min_hold_profit, min_hold_profit_index, max_hold_profit, max_hold_profit_index
import math
from typing import List
from rainiee_lib.dataframe import pandas_df
class Order(object):
    def construct(self, index : int, symbol : str, order_qty : float, order_price : float, buy_order : bool, ext={}):
        self.index = index
        self.symbol = symbol
        self.order_qty = int(math.floor(order_qty / 100.0)) * 100 #取整批最小100股交易
        self.order_price = order_price
        #默认在固定价格全部成交
        self.commision = 0.0005 #千分之一综合交易成本手续费
        self.buy_order = buy_order
        self.ext = ext

    """
    获取总成交金额（含手续费）
    """
    def get_filled_amount(self) -> float:#假设全部成交
        if(self.buy_order):
            return self.order_qty * self.order_price * (1 + self.commision)
        else:
            return self.order_qty * self.order_price * (1 - self.commision)

class OrderEntries(object):
    def construct(self, orders : List[Order]):
        self.orders = orders

    def get_orders_df(self):
        return pandas_df.get_df_obj_list(self.orders)

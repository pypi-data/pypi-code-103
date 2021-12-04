from typing import List, Dict
import pandas as pd

from rainiee_lib.objects.orders import order


class HoldingEntries(object):
    def construct(self,symbol :str, holding_qty : int, holding_price : float):
        self.symbol = symbol
        # 当前持仓数量
        self.holding_qty = 0
        # 当前持仓成本
        self.holding_price = 0
        # 总投入金额
        self.total_amt = 0
        # 浮动盈亏
        self.profit_loss_amt = 0

    def get_holding_return(self, curr_price) -> float:
        if self.holding_qty == 0:
            return self.profit_loss_amt
        return self.holding_qty * (curr_price - self.holding_price) + self.profit_loss_amt

    def place_order(self, order_obj : order.Order):
        if order_obj.buy_order:#买入
            total_qty = self.holding_qty + order_obj.order_qty
            self.holding_price = (self.holding_price * self.holding_qty + order_obj.get_filled_amount()) / total_qty
            self.holding_qty = total_qty
            self.total_amt = self.total_amt + order_obj.get_filled_amount()
        else:#卖出
            if (self.holding_qty < order_obj.order_qty):
                print("报错，卖出数量应小于持有数量")
                return None
            else:
                total_qty = self.holding_qty - order_obj.order_qty
                self.holding_price =  (self.holding_price * self.holding_qty - order_obj.get_filled_amount())/total_qty
                self.holding_qty = self.holding_qty - order_obj.order_qty
                self.profit_loss_amt = self.profit_loss_amt + order_obj.get_filled_amount()

class PortfolioHolding(object):
    #当有unique key的时候需要用map进行key的索引
    def construct(self, portf_holdings_map : Dict[str,HoldingEntries]):
        self.portf_holdings_map = portf_holdings_map
        self.portf_holdings_profit_map = {}

    def construct_from_list(self, portf_holdings : List[HoldingEntries]):
        self.portf_holdings_map = {x.symbol: x for x in portf_holdings}

    def rebalance(self, order_obj : order.Order):
        if order_obj.symbol in self.portf_holdings_map.keys():
            self.get_holding_entry(order_obj.symbol).place_order(order_obj)
        else:
            holding_entry = HoldingEntries()
            holding_entry.construct(order_obj.symbol, 0, 0)
            holding_entry.place_order(order_obj)
            self.portf_holdings_map.update({holding_entry.symbol:holding_entry})

    def get_holding_entry(self, symbol : str) -> HoldingEntries:
        return self.portf_holdings_map.get(symbol)


    def get_all_holding_entry(self) -> dict:
        return self.portf_holdings_map

    def get_portf_holding_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.portf_holdings_map,orient="index")

 

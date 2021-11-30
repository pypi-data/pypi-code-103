"""
Unsure if I'm going to add more functions here so todo on this docstring
"""

from typing import List


def buy_and_sell_a_stock_once(prices: List[float]) -> float:
    """
    solves https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
    """
    if len(prices) == 0:
        return 0

    max_profit = float("-inf")
    min_price = prices[0]

    for price in prices:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    return max_profit

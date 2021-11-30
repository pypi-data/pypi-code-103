from interviewing.questions import buy_and_sell_a_stock_once


def test_when_price_only_goes_up():
    prices = [1, 2, 3, 4]
    assert buy_and_sell_a_stock_once(prices) == 3


def test_when_price_only_goes_down():
    prices = [4, 3, 2, 1]
    assert buy_and_sell_a_stock_once(prices) == 0


def test_when_no_prices():
    prices = []
    assert buy_and_sell_a_stock_once(prices) == 0


def test_when_only_one_price():
    prices = [7]
    assert buy_and_sell_a_stock_once(prices) == 0


def test_doesnt_sell_before_buying():
    prices = [100, 1, 2]
    assert buy_and_sell_a_stock_once(prices) == 1

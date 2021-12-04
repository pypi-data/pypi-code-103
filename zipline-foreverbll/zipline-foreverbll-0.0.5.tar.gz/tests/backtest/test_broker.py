import pytest
from foreverbull_core.models.finance import OrderStatus, Portfolio

from app.backtest.exceptions import BrokerError


@pytest.mark.skip(reason="still dont know how to test this, TODO")
def test_can_trade(running_engine, broker, asset):
    new_day, finish = running_engine()
    new_day()
    broker._can_trade(asset)
    finish()


def test_can_trade_unknown_asset(running_engine, broker, asset):
    new_day, finish = running_engine()
    new_day()
    asset.symbol = "Ljungskile Pizzeria"
    with pytest.raises(BrokerError, match=".*Symbol 'LJUNGSKILE PIZZERIA' was not found"):
        broker._can_trade(asset)
    finish()


def test_order(running_engine, broker, order):
    _, finish = running_engine()
    order = broker._order(order)
    finish()
    assert len(order.id) > 5
    assert order.status == OrderStatus.OPEN


def test_order_unknown_asset(running_engine, broker, order):
    new_day, finish = running_engine()
    new_day()
    order.asset.symbol = "Ljungskile Pizzeria"
    with pytest.raises(BrokerError, match=".*Symbol 'LJUNGSKILE PIZZERIA' was not found"):
        broker._order(order)
    finish()


def test_get_order(running_engine, broker, order):
    new_day, finish = running_engine()
    broker._order(order)
    new_day()
    new_day()
    order = broker._get_order(order)
    finish()
    assert order.status == OrderStatus.FILLED


def test_get_order_unknown_order_id(running_engine, broker, order):
    new_day, finish = running_engine()
    new_day()
    order.id = "asdf"
    with pytest.raises(BrokerError, match="order asdf not found"):
        broker._get_order(order)
    finish()


def test_get_open_orders(running_engine, broker, order):
    new_day, finish = running_engine()
    broker._order(order)
    new_day()
    new_day()
    orders = broker._get_open_orders()
    finish()
    assert len(orders) == 1


def test_cancel_order(running_engine, broker, order):
    order.limit_price = 1
    order.stop_price = 1
    new_day, finish = running_engine()
    new_day()
    placed_order = broker._order(order)
    assert placed_order.status == OrderStatus.OPEN
    new_day()
    cancelled_order = broker._cancel_order(order)
    finish()
    assert cancelled_order.status == OrderStatus.CANCELLED


def test_cancel_order_unknown_order_id(running_engine, broker, order):
    new_day, finish = running_engine()
    new_day()
    order.id = "asdf"
    with pytest.raises(BrokerError, match="order asdf not found"):
        broker._cancel_order(order)
    finish()


def test_get_portfolio(running_engine, broker):
    _, finish = running_engine()
    finish()
    portfolio = broker._get_portfolio()
    assert type(portfolio) is Portfolio

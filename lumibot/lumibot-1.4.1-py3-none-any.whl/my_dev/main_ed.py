from datetime import datetime
from time import time

import pandas as pd
from credentials import InteractiveBrokersConfig
from strategies.ed_bot import EdBot

from lumibot.backtesting import PandasDataBacktesting
from lumibot.brokers import InteractiveBrokers
from lumibot.entities import Asset, Data
from lumibot.traders import Trader

# Choose your budget and log file locations
budget = 50000
strategy_name = "EdBot"

####
# Backtest
####

df = pd.read_csv(f"eurchf.csv")
df = df.set_index("time")
df.index = pd.to_datetime(df.index)
asset = Asset(
    symbol="EUR",
    currency="CHF",
    asset_type="forex",
)
pandas_data = {}
pandas_data[asset] = Data(
    asset,
    df,
    timestep="minute",
)

# Pick the date range you want to backtest
backtesting_start = datetime.datetime(2021, 7, 2)
backtesting_end = datetime.datetime(2021, 7, 20)

# Run the backtesting
EdBot.backtest(
    strategy_name,
    budget,
    PandasDataBacktesting,
    backtesting_start,
    backtesting_end,
    pandas_data=pandas_data,
)


####
# Run the strategy
####

trader = Trader()
broker = InteractiveBrokers(InteractiveBrokersConfig)

strategy = EdBot(
    name=strategy_name,
    budget=budget,
    broker=broker,
)
trader.add_strategy(strategy)
# trader.run_server()
trader.run_all()

# Password: hjkjdasug46w7#%%8w99

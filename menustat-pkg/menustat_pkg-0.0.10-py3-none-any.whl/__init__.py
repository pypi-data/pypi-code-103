"""Top-level package for MenuStat."""

import faulthandler

import warnings
import pandas


faulthandler.enable()

pandas.set_option("min_rows", 10)
pandas.set_option('display.max_columns', 15)
pandas.set_option("max_colwidth", 50)
pandas.set_option("display.width", 300)

warnings.filterwarnings("ignore", 'This pattern has match groups')

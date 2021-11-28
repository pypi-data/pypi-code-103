"""
kabutobashiにおいて、株に関する操作をする際に基本となるデータ構造を保持する。

- データ収集時に主に利用

  - StockIpo
  - Weeks52HighLow

- 分析時に主に利用

  - StockDataSingleDay
  - StockDataSingleCode
  - StockDataMultipleCode
  - StockDataProcessed
  - StockDataParameterized
"""
from .stock_data_processed import StockDataParameterized, StockDataProcessed
from .stock_data_raw import StockDataMultipleCode, StockDataRepository, StockDataSingleCode, StockDataSingleDay
from .stock_ipo import StockIpo
from .weeks_52_high_low_info import Weeks52HighLow

"""
Method modules provide technical analysis for stock chart.

- technical analysis

  - ADX
  - BollingerBands
  - Fitting
  - Ichimoku
  - MACD
  - Momentum
  - PsychoLogical
  - SMA
  - Stochastics

- other

  - Basic: only used `parameterize`

"""
from .adx import ADX
from .basic import Basic
from .bollinger_bands import BollingerBands
from .fitting import Fitting
from .ichimoku import Ichimoku
from .macd import MACD
from .method import Method
from .momentum import Momentum
from .psycho_logical import PsychoLogical
from .sma import SMA
from .stochastics import Stochastics

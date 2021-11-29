import os
import threading
from collections import namedtuple

import pandas as pd
import pytz
import six
from foreverbull_core.models.backtest import EngineConfig
from foreverbull_core.models.finance import Asset
from zipline import TradingAlgorithm
from zipline.data import bundles
from zipline.data.data_portal import DataPortal
from zipline.errors import SymbolNotFound
from zipline.extensions import load
from zipline.finance import metrics
from zipline.finance.blotter import Blotter
from zipline.finance.trading import SimulationParameters
from zipline.utils.calendar_utils import get_calendar
from zipline.utils.run_algo import BenchmarkSpec, _RunAlgoError

from .exceptions import ConfigError

Config = namedtuple(
    "config", "data_portal, trading_calendar, sim_params, metrics_set, blotter, benchmark_returns, benchmark_sid"
)
Assets = namedtuple("assets", "assets, benchmark")


class Engine(threading.Thread):
    _config = None

    def __init__(self, bundle="yahoo_demo_bundle"):
        self.assets = None
        self.bundle = bundle
        self.bundle_data = None
        self.trading_algorithm = None
        self.initialize = None
        self.handle_data = None
        self.analyze = None
        self.bundle_data = bundles.load(
            self.bundle,
            os.environ,
            None,
        )
        super(Engine, self).__init__()

    def set_callbacks(self, initialize, handle_data, analyze) -> None:
        self.initialize = initialize
        self.handle_data = handle_data
        self.analyze = analyze

    @property
    def configured(self) -> bool:
        return False if Engine._config is None else True

    def configure(self, config: EngineConfig) -> None:
        Engine._config = config
        try:
            start_date = pd.Timestamp(config.start_date, tz=config.timezone)
            end_date = pd.Timestamp(config.end_date, tz=config.timezone)
        except pytz.exceptions.UnknownTimeZoneError as e:
            raise ConfigError(repr(e))
        self.bundle_data = bundles.load(
            self.bundle,
            os.environ,
            None,
        )
        try:
            benchmark_spec = BenchmarkSpec(None, None, None, benchmark_symbol=config.benchmark, no_benchmark=None)
            benchmark_returns, benchmark_sid = benchmark_spec.resolve(
                asset_finder=self.bundle_data.asset_finder,
                start_date=start_date,
                end_date=end_date,
            )
        except _RunAlgoError as e:
            raise ConfigError(repr(e))
        trading_calendar = get_calendar("NYSE")
        data_portal = DataPortal(
            self.bundle_data.asset_finder,
            trading_calendar=trading_calendar,
            first_trading_day=self.bundle_data.equity_minute_bar_reader.first_trading_day,
            equity_minute_reader=self.bundle_data.equity_minute_bar_reader,
            equity_daily_reader=self.bundle_data.equity_daily_bar_reader,
            adjustment_reader=self.bundle_data.adjustment_reader,
        )
        sim_params = SimulationParameters(
            start_session=start_date,
            end_session=end_date,
            trading_calendar=trading_calendar,
            capital_base=100000,
            data_frequency="daily",
        )
        metrics_set = "default"
        blotter = "default"
        if isinstance(metrics_set, six.string_types):
            try:
                metrics_set = metrics.load(metrics_set)
            except ValueError as e:
                raise ConfigError(repr(e))

        if isinstance(blotter, six.string_types):
            try:
                blotter = load(Blotter, blotter)
            except ValueError as e:
                raise ConfigError(repr(e))
        trading_config = Config(
            data_portal, trading_calendar, sim_params, metrics_set, blotter, benchmark_returns, benchmark_sid
        )
        self.assets = Assets(config.assets, config.benchmark)
        self.trading_algorithm = TradingAlgorithm(
            namespace={},
            data_portal=trading_config.data_portal,
            trading_calendar=trading_config.trading_calendar,
            sim_params=trading_config.sim_params,
            metrics_set=trading_config.metrics_set,
            blotter=trading_config.blotter,
            benchmark_returns=trading_config.benchmark_returns,
            benchmark_sid=trading_config.benchmark_sid,
            initialize=self.initialize,
            handle_data=self.handle_data,
            analyze=self.analyze,
        )
        self.trading_algorithm.assets = []
        try:
            for asset in self.assets.assets:
                self.trading_algorithm.assets.append(self.trading_algorithm.symbol(asset))
        except SymbolNotFound as e:
            raise ConfigError(repr(e))
        self.trading_algorithm.set_benchmark(self.trading_algorithm.symbol(self.assets.benchmark))

    def _get_all_assets(self) -> dict:
        assets = []
        asset_list = self.bundle_data.asset_finder.retrieve_all(self.bundle_data.asset_finder.sids)
        for entry in asset_list:
            assets.append(Asset.create(entry))
        return {"assets": assets}

    def run(self) -> None:
        if self._config:
            self.configure(self._config)
        else:
            raise ConfigError("Missing config")
        self.trading_algorithm.run()

    def stop(self) -> None:
        return None

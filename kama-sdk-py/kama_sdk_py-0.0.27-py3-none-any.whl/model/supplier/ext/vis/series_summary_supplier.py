from functools import cached_property
from typing import Optional, List, Dict

from kama_sdk.core.core.types import TimeseriesDataPoint, SimpleSeriesSummary
from kama_sdk.model.humanizer.quantity_humanizer import QuantityHumanizer
from kama_sdk.model.supplier.base.supplier import Supplier


class SeriesSummarySupplier(Supplier):

  @cached_property
  def time_series(self) -> List[TimeseriesDataPoint]:
    v = self.get_source_data()
    # print("SOURCE DATA")
    # print(v)
    return v

  @cached_property
  def reducer_type(self) -> str:
    return self.get_attr(REDUCER_FUNC_KEY, 'last')

  def change_direction(self) -> str:
    try:
      count = len(self.time_series)
      if count >= 2:
        last = _last_value(self.time_series)
        avg = _series_avg(self.time_series)
        return 'up' if last - avg > 0 else 'down'
    except:
      return ''

  @cached_property
  def good_direction(self) -> str:
    return self.get_attr(GOOD_DIRECTION_KEY, 'up')

  @cached_property
  def humanizer(self) -> QuantityHumanizer:
    return self.inflate_child(
      QuantityHumanizer,
      attr=HUMANIZER_KEY,
      safely=True
    ) or QuantityHumanizer({})

  # noinspection PyBroadException
  def summary_quant(self) -> Optional[float]:
    try:
      if self.reducer_type == 'last':
        return _last_value(self.time_series)
      elif self.reducer_type == 'sum':
        return _series_sum(self.time_series)
    except:
      return None

  def summary_value(self) -> str:
    return self.humanizer.humanize_expr(self.summary_quant())

  def humanized_series(self) -> List[Dict]:
    return [humanize_datapoint(d, self.humanizer) for d in self.time_series]

  def resolve(self) -> Optional[SimpleSeriesSummary]:
    if self.time_series:
      return SimpleSeriesSummary(
        series=self.time_series,
        humanized_series=self.humanized_series(),
        direction=self.change_direction(),
        good_direction=self.good_direction,
        summary_value=self.summary_value()
      )
    else:
      return None


def humanize_datapoint(datapoint, humanizer: QuantityHumanizer):
  return {
    **datapoint,
    'value': humanizer.humanize_quantity(datapoint['value'])
  }


def _last_value(series: List[Dict]) -> Optional[float]:
  if len(series) > 0:
    return series[len(series) - 1]['value']
  else:
    return None


def _series_sum(series: List[TimeseriesDataPoint]) -> float:
  return sum([float(d['value'] or 0) for d in series])


def _series_avg(series: List[TimeseriesDataPoint]) -> float:
  try:
    return _series_sum(series) / len(series)
  except ValueError:
    return 0.0


DATA_KEY = 'time_series_data'
REDUCER_FUNC_KEY = 'reducer'
HUMANIZER_KEY = 'humanizer'
GOOD_DIRECTION_KEY = 'good_direction'

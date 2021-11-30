from typing import Optional, Dict, List, Callable

from kama_sdk.model.supplier.base.supplier import Supplier


class TimeseriesAggregationSupplier(Supplier):

  def get_source_data(self) -> Optional[List[Dict]]:
    return super(TimeseriesAggregationSupplier, self).get_source_data()

  def get_outer_aggregator(self) -> str:
    return self.get_attr(INNER_AGG_FUNC_KEY, backup='sum')

  def get_inner_aggregator(self) -> str:
    return self.get_attr(OUTER_AGG_FUNC_KEY, backup='sum')

  def t_point(self) -> str:
    return self.get_attr(T_POINT_KEY, backup='n-1', lookback=False)

  def _compute(self):
    if timeseries := self.get_source_data():
      subset = outer(timeseries, self.t_point())
      scalars = nd_to_1d(subset, self.get_inner_aggregator())
      return _1d_to_1(scalars, self.get_outer_aggregator())


def _1d_to_1(data: List[float], agg_type: str) -> float:
  if agg_func := simple_agg(agg_type):
    return agg_func(data)
  else:
    print(f"FATAL! unrecognized outer aggregator {agg_type}")
    return 0

def nd_to_1d(data: List[Dict], agg_type: str) -> List[float]:
  if agg_func := simple_agg(agg_type):
    def big_agg(data_point: Dict):
      quant_values = []
      for key, value in data_point.items():
        if not key == 'timestamp':
          quant_values.append(float(value))
      return agg_func(quant_values)
    return list(map(big_agg, data))
  else:
    print(f"FATAL! unrecognized inner aggregator {agg_type}")
    return []


def simple_agg(agg_type: str) -> Optional[Callable[[List[float]], float]]:
  if agg_type == 'sum':
    return sum
  elif agg_type in ['avg', 'average']:
    return lambda values: sum(values) / len(values)
  else:
    return None


def outer(data: List, t_expr: str) -> List:
  if " to " in t_expr:
    parts = t_expr.split(" to ")
    i_start = parse_single(parts[0], len(data))
    i_end = parse_single(parts[1], len(data))
  else:
    i_start = parse_single(t_expr, len(data))
    i_end = i_start + 1
  return data[i_start:i_end]

def parse_single(t_expr: str, list_len: int) -> int:
  if t_expr == 'n':
    return list_len
  if t_expr.startswith("n-"):
    return list_len - int(t_expr.split("n-")[1])
  else:
    return int(t_expr)


INNER_AGG_FUNC_KEY = 'inner_aggregator'
OUTER_AGG_FUNC_KEY = 'outer_aggregator'
T_POINT_KEY = 't'

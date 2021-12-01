from kama_sdk.model.supplier.base import supplier
from kama_sdk.model.supplier.ext.vis import timeseries_aggregation_supplier as mod
from kama_sdk.model.supplier.ext.vis.timeseries_aggregation_supplier import TimeseriesAggregationSupplier
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestTimeseriesAggregatorSupplier(ClusterTest):

  def test_outer(self):
    _list = ['a', 'b', 'c']
    self.assertEqual(['a'], mod.outer(_list, "0"))
    self.assertEqual(['a'], mod.outer(_list, "0 to 1"))
    self.assertEqual(['a', 'b'], mod.outer(_list, "0 to 2"))
    self.assertEqual(['c'], mod.outer(_list, "n-1"))
    self.assertEqual(['b', 'c'], mod.outer(_list, "1 to n"))

  def test_nd_to_1d(self):
    _list = data_one
    self.assertEqual([3.0, 7.0], mod.nd_to_1d(_list, 'sum'))
    self.assertEqual([1.5, 3.5], mod.nd_to_1d(_list, 'avg'))

  def test_compute(self):
    result = gen_model('sum', 'sum', 'n-1').resolve()
    self.assertEqual(7.0, result)

    result = gen_model('sum', 'sum', '0 to 3').resolve()
    self.assertEqual(10.0, result)

    result = gen_model('sum', 'avg', '0 to n').resolve()
    self.assertEqual(5.0, result)

    result = gen_model('avg', 'sum', '0 to n').resolve()
    self.assertEqual(5.0, result)


def gen_model(inner_agg, outer_agg, t):
  return TimeseriesAggregationSupplier.inflate({
    mod.INNER_AGG_FUNC_KEY: inner_agg,
    mod.OUTER_AGG_FUNC_KEY: outer_agg,
    mod.T_POINT_KEY: t,
    supplier.SRC_DATA_KEY: data_one
  })


data_one = [
  {'a': 1, 'b': '2', 'timestamp': 'bad'},
  {'a': 3, 'b': '4', 'timestamp': 'dab'}
]

import unittest

from mysutils.file import load_json

from myskutils.measure import Measure, MetricName, CI, Metric
from myskutils.plot import plot

Y_TRUES_FILE = 'test/trues.json'
Y_PRED_FILE = 'test/pred.json'
MEASURES_FILE = 'test/data.json'
CONF_95_FILE = 'test/conf_95.json'
CONF_99_FILE = 'test/conf_99.json'
result = {
    'accuracy': 0.7314814814814815, 'balanced_accuracy': 0.7336080586080586,
    'micro_f1': 0.7314814814814816, 'macro_f1': 0.6676911015978718, 'weighted_f1': 0.7064382543140714,
    'micro_precision': 0.7314814814814815, 'macro_precision': 0.6733602875112309,
    'weighted_precision': 0.7421737213403881, 'micro_recall': 0.7314814814814815,
    'macro_recall': 0.7197663971248877, 'weighted_recall': 0.7314814814814815,
    'micro_jaccard': 0.5766423357664233, 'macro_jaccard': 0.6027144762993819,
    'weighted_jaccard': 0.6215661910106355
}


class MyTestCase(unittest.TestCase):
    def test_format_values(self) -> None:
        y_trues, y_pred = load_json(Y_TRUES_FILE), load_json(Y_PRED_FILE)
        measure = Measure.from_evaluation(y_trues, y_pred)
        # self.assertDictEqual(result, measure.to_dict())  # add assertion here
        self.assertEqual(measure[MetricName.SIMPLE_ACCURACY].format(), '73.15')
        self.assertEqual(measure[MetricName.SIMPLE_ACCURACY].format(3), '73.148')
        self.assertEqual(measure[MetricName.SIMPLE_ACCURACY].format(0), '73')

    def test_print(self):
        measure = Measure.from_evaluation(load_json(Y_TRUES_FILE), load_json(Y_PRED_FILE))
        measure.print()
        measure.select('accuracy').print()
        self.assertEqual(True, True)  # add assertion here

    def test_confidence_interval(self) -> None:
        measures = [Measure.from_dict(eval) for eval in load_json(MEASURES_FILE)]

        ci_measures = Measure.confidence_score(measures, 0.95)
        self.assertEqual(str(ci_measures.select(MetricName.WEIGHTED_F1)),
                         'Measure(weighted_f1=0.6897580626192598±0.03565990800863161)')
        self.assertEqual(str(ci_measures.metric(MetricName.WEIGHTED_F1, 'BERT_MODEL')),
                         'BERT_MODEL=0.6897580626192598±0.03565990800863161')
        self.assertEqual(str(ci_measures.min_uncertainty()), 'balanced_accuracy=0.695702864876455±0.0315404522111038')
        self.assertEqual(str(ci_measures.max_uncertainty()), 'micro_jaccard=0.5316665991417848±0.040809554891851146')
        self.assertEqual(str(ci_measures.min_value()), 'micro_jaccard=0.5316665991417848±0.040809554891851146')
        self.assertEqual(str(ci_measures.max_value()), 'weighted_precision=0.7389542915931806±0.03589302220107715')
        self.assertEqual(str(ci_measures.min_value().in_interval(ci_measures.metrics)),
                         '[micro_jaccard=0.5316665991417848±0.040809554891851146, '
                         'macro_jaccard=0.5584330739064476±0.03740462144237966, '
                         'weighted_jaccard=0.602431880785639±0.035765269919655784]')
        self.assertEqual(str(ci_measures.max_value().in_interval(ci_measures.metrics)),
                         '[simple_accuracy=0.6925925925925926±0.03502136605451667, '
                         'balanced_accuracy=0.695702864876455±0.0315404522111038, '
                         'micro_f1=0.6925925925925926±0.03502136605451667, '
                         'weighted_f1=0.6897580626192598±0.03565990800863161, '
                         'micro_precision=0.6925925925925926±0.03502136605451667, '
                         'weighted_precision=0.7389542915931806±0.03589302220107715, '
                         'micro_recall=0.6925925925925926±0.03502136605451667, '
                         'weighted_recall=0.6925925925925926±0.03502136605451667]')
        plot(list(ci_measures.metrics))

    def test_ci_type(self) -> None:
        ci1 = CI(1.5, 0.25)
        self.assertEqual(str(ci1), '1.5±0.25')
        self.assertEqual(ci1.value, 1.5)
        self.assertEqual(ci1.ci, 0.25)
        self.assertEqual(ci1.min, 1.25)
        self.assertEqual(ci1.max, 1.75)
        self.assertIsNone(ci1.p)
        self.assertIsNone(ci1 ** 2)
        self.assertTupleEqual(ci1.interval, (1.25, 1.75))
        ci2 = CI.from_interval(2, 1.5, 0.95)
        self.assertEqual(ci2.value, 1.75)
        self.assertEqual(ci2.min, 1.5)
        self.assertEqual(ci2.max, 2)
        self.assertEqual(ci2.ci, 0.25)
        self.assertEqual(ci2.p, 0.95)
        self.assertEqual(ci2 ** 2, 0.9025)
        self.assertFalse(ci1.is_significant(ci2))
        self.assertTupleEqual(ci2.interval, (1.5, 2))
        ci3 = CI(1, 0.25, 0.99)
        ci4 = CI(1, 0.25, 0.99)
        self.assertTrue(ci2.is_significant(ci3))
        self.assertTrue(ci3.is_significant(ci2))
        self.assertTrue(ci4 == ci3)
        self.assertFalse(ci4 != ci3)
        self.assertTrue(ci2 > ci3)
        self.assertTrue(ci1 > ci3)
        self.assertTrue(ci1 >= ci3)
        self.assertFalse(ci1 <= ci3)
        self.assertFalse(ci1 < ci3)
        self.assertTupleEqual(tuple(ci1), (1.5, 0.25))
        self.assertTrue(ci1)
        self.assertTrue(ci2)
        self.assertFalse(CI(0, 0))
        self.assertEqual(float(ci1), 1.5)
        self.assertEqual(float(ci2), 1.75)
        self.assertEqual(hash(ci1), 3808642330255693810)
        self.assertNotIn(ci1, ci2)
        self.assertIn(CI(1.6, 0.1), ci1)
        self.assertIn(CI(1.5, 0.25), ci1)
        self.assertEqual(complex(1.5, 0.25), complex(ci1))


if __name__ == '__main__':
    unittest.main()

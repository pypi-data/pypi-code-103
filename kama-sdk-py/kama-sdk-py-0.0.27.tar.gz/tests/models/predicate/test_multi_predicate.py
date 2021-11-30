from kama_sdk.model.predicate import predicate as pred, multi_predicate
from kama_sdk.model.predicate.common_predicates import TruePredicate, FalsePredicate
from kama_sdk.model.predicate.multi_predicate import MultiPredicate
from kama_sdk.utils.unittest.base_classes import ClusterTest

mp = MultiPredicate
op = pred.OPERATOR_KEY
source = multi_predicate.PREDICATES_KEY

TRUE_REF = f"kind::{TruePredicate.__name__}"
FALSE_REF = f"kind::{FalsePredicate.__name__}"

class TestMultiPredicate(ClusterTest):

  def test_multi_predicate_ands_true(self):
    predicate = mp({op: 'and', source: [TRUE_REF]})
    self.assertTrue(predicate.resolve())

    predicate = mp({op: 'and', source: [TRUE_REF, TRUE_REF]})
    self.assertTrue(predicate.resolve())

    predicate = mp({op: 'and', source: []})
    self.assertTrue(predicate.resolve())

  def test_multi_predicate_ands_false(self):
    predicate = mp({op: 'and', source: [FALSE_REF]})
    self.assertFalse(predicate.resolve())

    predicate = mp({op: 'and', source: [FALSE_REF, FALSE_REF]})
    self.assertFalse(predicate.resolve())

    predicate = mp({op: 'and', source: [FALSE_REF, TRUE_REF]})
    self.assertFalse(predicate.resolve())

  def test_multi_predicate_ors_true(self):
    predicate = mp({op: 'or', source: [TRUE_REF]})
    self.assertTrue(predicate.resolve())

    predicate = mp({op: 'or', source: [TRUE_REF, FALSE_REF]})
    self.assertTrue(predicate.resolve())

  # def test_multi_predicate_ors(self):
  #   predicate = mp(operator='or', source=[False])
  #   self.assertFalse(predicate.resolve())
  #
  #   predicate = MultiPredicate(dict(operator='or', predicates=[]))
  #   self.assertFalse(predicate.resolve())
  #
  #   predicate = mp(operator='or', source=[True])
  #   self.assertTrue(predicate.resolve())
  #
  #   predicate = mp(operator='or', source=[f"get::{TruePredicate.__name__}"])
  #   self.assertTrue(predicate.resolve())
  #
  #   predicate = mp(operator='or',  source=[True, False])
  #   self.assertTrue(predicate.resolve())
  #
  #   predicate = MultiPredicate(dict(
  #     operator='or',
  #     predicates=[
  #       f"get::kind::{FalsePredicate.__name__}",
  #       False
  #     ]
  #   ))
  #   self.assertFalse(predicate.resolve())

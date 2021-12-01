from kama_sdk.model.predicate import predicate
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestPredicate(ClusterTest):

  def test_standard_comparison(self):
    self.assertTrue(comp('=', 1, 1))
    self.assertTrue(comp('=', True, True))
    self.assertTrue(comp('=', True, 'True'))
    self.assertTrue(comp('=', 'true', True))
    self.assertTrue(comp('=', 1, '1'))
    self.assertTrue(comp('=', '1', 1))
    self.assertFalse(comp('=', '1', '2'))
    self.assertTrue(comp('>', 2, 1))
    self.assertTrue(comp('<', 1, 2))
    self.assertTrue(comp('>=', 2, 2))
    self.assertTrue(comp('>=', 3, 2))
    self.assertTrue(comp('<=', 2, 2))
    self.assertTrue(comp('<=', 2, 3))
    self.assertTrue(comp('in', 1, [1, 2]))
    self.assertTrue(comp('in', 'fo', 'foo'))
    self.assertTrue(comp('contains', [1, 2], 1))
    self.assertFalse(comp('defined', '', None))
    self.assertFalse(comp('truthy', '', None))
    self.assertTrue(comp('truthy', 'True', None))
    self.assertFalse(comp('truthy', 'False', None))
    self.assertFalse(comp('truthy', False, None))
    self.assertTrue(comp('truthy', True, None))
    self.assertFalse(comp('defined', None, None))
    self.assertTrue(comp('defined', 'x', None))
    self.assertTrue(comp('undefined', '', None))

  def test_perform_comparison(self):
    self.assertTrue(comp('=', [1, 1], 1, 'each_true'))
    self.assertTrue(comp('=', [1, 2], 1, 'some_true'))
    self.assertFalse(comp('=', [1, 1], 1, 'each_false'))
    self.assertTrue(comp('=', [1, 2], 1, 'some_false'))

    self.assertFalse(comp('=', [1, 2], 1, 'each_true'))
    self.assertFalse(comp('=', [2, 2], 1, 'some_true'))
    self.assertTrue(comp('=', [2, 2], 1, 'each_false'))
    self.assertFalse(comp('=', [1, 1], 1, 'some_false'))

def comp(name, challenge, check_against, on_many=None) -> bool:
  return predicate.perform_comparison(
    name,
    challenge,
    check_against,
    on_many
  )

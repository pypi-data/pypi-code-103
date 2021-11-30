from kama_sdk.model.base.mc import ID_KEY
from kama_sdk.model.predicate.predicate import CHECK_AGAINST_KEY, CHALLENGE_KEY, TONE_KEY, REASON_KEY
from kama_sdk.model.variable.generic_variable import GenericVariable, VALIDATION_PREDS_KEY, VALUE_PATCH_KEY
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestGenericVariable(ClusterTest):

  def test_validate_when_valid(self):
    gv = GenericVariable.inflate(only_valid_var_desc)
    actual = gv.validate('foo')
    self.assertTrue(actual['met'])

  def test_validate_when_not_valid(self):
    gv = GenericVariable.inflate(mixed_valid_var_desc)
    actual = gv.validate('foo')
    self.assertFalse(actual['met'])
    self.assertEqual('warning', actual['tone'])
    self.assertEqual('because foo', actual['reason'])


eq_foo_pred_desc = {
  ID_KEY: 'eq-foo',
  CHECK_AGAINST_KEY: 'foo',
  CHALLENGE_KEY: f"get::self>>{VALUE_PATCH_KEY}"
}


eq_bar_pred_desc = {
  ID_KEY: 'eq-bar',
  CHECK_AGAINST_KEY: 'bar',
  TONE_KEY: 'warning',
  CHALLENGE_KEY: f"get::self>>{VALUE_PATCH_KEY}",
  REASON_KEY: "because ${get::self>>resolved_challenge}",
}

only_valid_var_desc = {
  VALIDATION_PREDS_KEY: [
    eq_foo_pred_desc
  ]
}

mixed_valid_var_desc = {
  VALIDATION_PREDS_KEY: [
    eq_foo_pred_desc,
    eq_bar_pred_desc
  ]
}

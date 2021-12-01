from kama_sdk.model.operation.field import Field
from kama_sdk.model.variable import generic_variable
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestField(ClusterTest):

  def test_synthesize_variable(self):
    # models_manager.clear(restore_defaults=True)
    field = Field({
      generic_variable.DEFAULT_VALUE_KEY: 'def',
      generic_variable.INPUT_MODEL_KEY: {
        'id': 'input'
      },
      generic_variable.VALIDATION_PREDS_KEY: [
        f"expr::equals?x"
      ]
    })
    synth_variable = field.get_variable()
    self.assertEqual('def', synth_variable.get_default_value())
    self.assertEqual('input', synth_variable.get_input_model().get_id())
    self.assertEqual(1, len(synth_variable.get_patched_validation_predicates('x')))
    self.assertTrue(synth_variable.validate('x')['met'])
    self.assertFalse(synth_variable.validate('y')['met'])

  def test_delegate_inside(self):
    field = Field(dict(
      id='bar',
      title='t',
      info='i'
    ))
    self.assertEqual('bar', field.get_id())
    self.assertEqual('t', field.get_title())
    self.assertEqual('i', field.get_info())

  def test_delegate_outside(self):
    field = Field(dict(
      id='foo',
      variable=dict(
        title='generic-t',
        info='generic-i'
      )
    ))

    self.assertEqual('generic-t', field.get_title())
    self.assertEqual('generic-i', field.get_info())

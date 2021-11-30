from kama_sdk.core.core import consts
from kama_sdk.core.core.consts import TARGET_STANDARD, TARGET_INLINE, TARGET_STATE, TARGET_PREFS
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.base import mc
from kama_sdk.model.base.common import PREDICATE_KEY, VALUE_KEY
from kama_sdk.model.base.mc import ID_KEY, ATTR_KW, PATCH_KEY, KIND_KEY
from kama_sdk.model.operation import field as field_module
from kama_sdk.model.operation import step as step_mod
from kama_sdk.model.operation.field import Field
from kama_sdk.model.operation.operation_state import OperationState
from kama_sdk.model.operation.step import Step, gen_downstream_patches
from kama_sdk.model.predicate import predicate
from kama_sdk.model.predicate.common_predicates import TruePredicate
from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.model.supplier.base import supplier
from kama_sdk.model.supplier.base.misc_suppliers import MergeSupplier
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.model.supplier.base.switch import Switch
from kama_sdk.model.variable import generic_variable
from kama_sdk.utils.unittest import helper
from kama_sdk.utils.unittest.base_classes import KamaTest


class TestStep(KamaTest):
  def test_field_patch_propagation(self):
    step = Step(step1_config)
    op_state = OperationState('xxx', 'yyy')
    step_state = op_state.gen_step_state(step, keep=True)
    step_state.state_assigns = {'k': {'s1': 's1v'}}

    patched_fields = step.inflate_children(
      Field,
      **{
        ATTR_KW: step_mod.FIELDS_KEY,
        PATCH_KEY: gen_downstream_patches(op_state, {'i1': 'i1v'})
      }
    )

    actual1 = patched_fields[0].resolve_attr_value("get::self>>inputs")
    self.assertEqual({'i1': 'i1v'}, actual1)

    actual2 = patched_fields[0].resolve_attr_value("get::self>>op_state")
    self.assertEqual({'k': {'s1': 's1v'}}, actual2)

  def test_visible_fields_one(self):
    op_state, step, step_state = prep_vis_test()
    result = step.filter_visible_fields({}, op_state)
    self.assertEqual(['fields.f1'], ids(result))

  def test_visible_fields_two(self):
    op_state, step, step_state = prep_vis_test()
    inputs = {'fields': {'f2': 'not-f2'}}
    result = step.filter_visible_fields(inputs, op_state)
    self.assertEqual(['fields.f1'], ids(result))

  def test_visible_fields_three(self):
    op_state, step, step_state = prep_vis_test()
    inputs = {'fields': {'f2': 'f2'}}
    result = step.filter_visible_fields(inputs, op_state)
    self.assertEqual(['fields.f1', 'fields.f2'], ids(result))

  def test_visible_fields_four(self):
    op_state, step, step_state = prep_vis_test()
    step_state.state_assigns = {'fields': {'f3': 'f3'}}
    inputs = {'fields': {'f2': 'f2'}}
    result = step.filter_visible_fields(inputs, op_state)
    self.assertEqual(['fields.f1', 'fields.f2', 'fields.f3'], ids(result))

  def test_validate_field(self):
    step = Step(step1_config)
    op_state = OperationState('xxx', 'yyy')
    op_state.gen_step_state(step, keep=True)

    result = lambda f, v: step.validate_field(f, v, op_state)['met']
    self.assertTrue(result('fields.f1', None))
    self.assertFalse(result('fields.f2', 'wrong'))
    self.assertTrue(result('fields.f2', 'right'))

  def test_assemble_action_config(self):
    op_state = OperationState('', '')
    step = Step(step1_config)
    op_state.gen_step_state(step, keep=True)

    buckets = {
      consts.TARGET_STANDARD: {'c0': {'c': 'c'}},
      consts.TARGET_INLINE: {'i': 'i'},
      consts.TARGET_PREFS: {}
    }

    config = step.gen_final_action(op_state, buckets).serialize()
    self.assertEqual('Action', config['kind'])
    self.assertEqual('nested-action', config['id'])
    self.assertEqual({'i': 'i'}, config['commit'][consts.TARGET_INLINE])
    self.assertEqual({'c0': {'c': 'c'}}, config['commit'][consts.TARGET_STANDARD])

  def test_next_step_id(self):
    op_state, step, step_state = prep_vis_test()
    self.assertIsNone(step.compute_next_step_id(op_state))

    op_state.step_states[0].state_assigns = {"goto": 'option_one'}
    self.assertEqual('option_one', step.compute_next_step_id(op_state))

    op_state.step_states[0].state_assigns = {"goto": 'option_two'}
    self.assertEqual('option_two', step.compute_next_step_id(op_state))

  def test_final_partitioning(self):
    op_state, step, step_state = prep_vis_test(step2_config)
    ss1 = op_state.gen_step_state(step)
    ss1.chart_assigns = {}

    inputs = {
      'a': {'f1': 'v1', 'f2': 'v2'},
      'b': {'f3': 'v3'},
      'f4': 'v4'
    }

    expect = {
      TARGET_STANDARD: {'a': {'f1': 'v1'}, 'extra': 'extra'},
      TARGET_INLINE: {'foo': {'bar': {'baz': 'v1'}}},
      TARGET_STATE: {},
      TARGET_PREFS: {'f4': 'v4'}
    }

    actual = step.partition_vars(inputs, op_state)
    self.assertEqual(expect, actual)

  def test_partition_vars_by_field(self):
    step = Step(step2_config)

    inputs = {
      'a': {'f1': 'v1', 'f2': 'v2'},
      'b': {'f3': 'v3'},
      'f4': 'v4'
    }

    expected = {
      TARGET_STANDARD: {'a': {'f1': 'v1'}},
      TARGET_INLINE: {'a': {'f2': 'v2'}},
      TARGET_STATE: {'b': {'f3': 'v3'}},
      TARGET_PREFS: {'f4': 'v4'}
    }

    op_state = helper.one_step_state(step).parent_op
    actual = step._partition_vars_by_field(inputs, op_state)
    self.assertEqual(expected, actual)


step1_config = {
  mc.ID_KEY: 'step',
  step_mod.NEXT_STEP_KEY: {
    KIND_KEY: Switch.__name__,
    supplier.SRC_DATA_KEY: [
      {
        PREDICATE_KEY: {
          KIND_KEY: Predicate.__name__,
          predicate.CHALLENGE_KEY: "get::self>>op_state->.goto",
          predicate.CHECK_AGAINST_KEY: 'option_one'
        },
        VALUE_KEY: 'option_one'
      },
      {
        PREDICATE_KEY: {
          KIND_KEY: Predicate.__name__,
          predicate.CHALLENGE_KEY: "get::self>>op_state->.goto",
          predicate.CHECK_AGAINST_KEY: 'option_two'
        },
        VALUE_KEY: 'option_two'
      }
    ]
  },
  step_mod.FIELDS_KEY: [
    {
      ID_KEY: 'fields.f1',
      field_module.TARGET_KEY: consts.TARGET_STANDARD,
      generic_variable.VALIDATION_PREDS_KEY: [
        f"kind::{TruePredicate.__name__}"
      ]
    },
    {
      ID_KEY: 'fields.f2',
      field_module.TARGET_KEY: consts.TARGET_INLINE,
      field_module.VISIBLE_KEY: {
        KIND_KEY: Predicate.__name__,
        predicate.CHALLENGE_KEY: "get::self>>inputs->.fields.f2",
        predicate.CHECK_AGAINST_KEY: 'f2'
      },
      generic_variable.VALIDATION_PREDS_KEY: [
        {
          predicate.CHECK_AGAINST_KEY: 'right'
        }
      ]
    },
    {
      mc.ID_KEY: 'fields.f3',
      field_module.TARGET_KEY: consts.TARGET_STATE,
      field_module.VISIBLE_KEY: {
        KIND_KEY: Predicate.__name__,
        predicate.CHALLENGE_KEY: "get::self>>op_state->.fields.f3",
        predicate.CHECK_AGAINST_KEY: 'f3'
      }
    }
  ],
  step_mod.ACTION_KEY: {
    mc.KIND_KEY: Supplier.__name__,
    supplier.SRC_DATA_KEY: {
      KIND_KEY: Action.__name__,
      ID_KEY: 'nested-action'
    }
  }}


step2_config = {
  'fields': [
    {'id': 'a.f1', 'target': TARGET_STANDARD},
    {'id': 'a.f2', 'target': TARGET_INLINE},
    {'id': 'b.f3', 'target': TARGET_STATE},
    {'id': 'f4', 'target': TARGET_PREFS}
  ],
  'commit': {
    TARGET_STANDARD: {
      'kind': MergeSupplier.__name__,
      'source': [
        f'get::self>>default_commit->.{TARGET_STANDARD}',
        {'extra': 'extra'}
      ]
    },
    consts.TARGET_INLINE: {
      'foo.bar.baz': f'get::self>>inputs->.a.f1'
    },
    consts.TARGET_STATE: {}
  }
}


def prep_vis_test(step_desc=None):
  step_desc = step_desc or step1_config
  op_state = OperationState('xxx', 'yyy')
  step = Step(step_desc)
  step_state = op_state.gen_step_state(step, keep=True)
  step_state.state_assigns = {}
  return op_state, step, step_state


def ids(models):
  return [m.get_id() for m in models]

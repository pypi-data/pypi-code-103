from typing import List, Dict, Optional

from kama_sdk.core.core import job_client, consts
from kama_sdk.core.core.consts import TARGET_TYPES, COMMIT_TARGET_TYPES
from kama_sdk.core.core.types import CommitOutcome, PredEval
from kama_sdk.model.action.base.action import Action, TELEM_EVENT_TYPE_KEY, OP_STEP_EVENT_TYPE
from kama_sdk.model.action.base.multi_action import MultiAction, SUB_ACTIONS_KEY
from kama_sdk.model.base import mc
from kama_sdk.model.base.mc import CONFIG_SPACE_KEY
from kama_sdk.model.base.model import Model
from kama_sdk.model.operation.field import Field
from kama_sdk.model.operation.operation_state import OperationState
from kama_sdk.model.operation.step_state import StepState
from kama_sdk.utils import utils
from kama_sdk.utils.logging import lwar, lerr

TOS = OperationState
TSS = StepState
TOOS = Optional[OperationState]
TCO = CommitOutcome


class Step(Model):

  def sig(self) -> str:
    parent = self.get_parent()
    parent_id = parent.get_id() if parent else 'orphan'
    return f"{parent_id}::{self.get_id()}"

  def does_run_action(self) -> bool:
    return bool(self._config.get(ACTION_KEY))

  def compute_next_step_id(self, op_state: TOS) -> Optional[str]:
    self.patch(gen_downstream_patches(op_state, {}))
    return self.get_attr(NEXT_STEP_KEY)

  def get_fields(self) -> List[Field]:
    return self.inflate_children(Field, attr=FIELDS_KEY)

  def validate_field(self, field_id: str, value: str, op_state: TOS) -> PredEval:
    fields = self.inflate_children(
      Field,
      attr=FIELDS_KEY,
      patches=gen_downstream_patches(op_state, {field_id: value})
    )
    finder = lambda f: f.get_id() == field_id
    field = next(filter(finder, fields), None)
    return field.get_variable().validate(value)

  def filter_visible_fields(self, assignments, op_state: TOS) -> List[Field]:
    patch = gen_downstream_patches(op_state, assignments)
    kwargs = {mc.ATTR_KW: FIELDS_KEY, mc.PATCH_KEY: patch}
    fields = self.inflate_children(Field, **kwargs)
    return [f for f in fields if f.compute_visibility()]

  def run(self, assigns: Dict, state: StepState) -> Optional[str]:
    buckets = self.partition_vars(assigns, state.parent_op)
    state.notify_vars_assigned(buckets)

    if action := self.gen_final_action(state.parent_op, buckets):
      action_config = action2config(action)
      return job_client.enqueue_action(action_config)
    else:
      return None

  def gen_final_action(self, op_state: OperationState, buckets) -> Optional[Action]:
    """
    In case the action has dynamic parts to it, we must resolve it
    before it runs in a different process (no shared memory). Also merges in
    event-telem config. Omits the unmarshalable 'context' of the config.
    @param op_state: step state that IFTT might use to make resolution
    @param buckets: value buckets eg chart, inline, state
    @return: un-IFTT'ed config dict for the action
    """

    # default_commit_bundle = {t: buckets[t] for t in COMMIT_TARGET_TYPES}
    # self.patch({DEFAULT_COMMIT_KEY: default_commit_bundle})
    # commit_bundle = self.get_local_attr(COMMIT_KEY) or default_commit_bundle
    commit_bundle = {t: buckets[t] for t in COMMIT_TARGET_TYPES}

    patch = {
      **gen_downstream_patches(op_state, {}),
      CONFIG_SPACE_KEY: self.get_config_space(),
      COMMIT_KEY: commit_bundle
    }

    return self.inflate_child(
      Action,
      attr=ACTION_KEY,
      safely=True,
      patch=patch
    ) if self.does_run_action() else None

  def partition_vars(self, inputs: Dict, op_state: TOS) -> Dict:
    self_patch = gen_downstream_patches(op_state, inputs)
    print(f"self patch 1 ---------------- {self_patch}")
    self.patch(self_patch)
    default_commit = self._partition_vars_by_field(inputs, op_state)

    self_patch2 = dict(default_commit=default_commit)

    print(f"self patch 2 ---------------- {self_patch2}")
    self.patch(self_patch2)

    commit_override = self.get_attr('commit', depth=100)

    print(f"pure overwrite ---------------- {commit_override}")

    bundle = sanitize_commit_bundle(commit_override, default_commit)

    print(f"fixed ---------------- {bundle}")

    return bundle

  def get_summary_descriptor(self, inputs: Dict, op_state) -> Optional[Dict]:
    self.patch(gen_downstream_patches(op_state, inputs))
    try:
      return self.get_attr(SUMMARY_DESCRIPTOR, lookback=False)
    except Exception as e:
      lerr(f"compute summary desc failed", exc=e)
      return None

  def _partition_vars_by_field(self, inputs: Dict, op_state: TOS) -> Dict:
    fields = self.filter_visible_fields(inputs, op_state)
    return {t: filter_inputs_by_type(fields, inputs, t) for t in TARGET_TYPES}


def gen_downstream_patches(op_state: OperationState, user_input: Dict):
  return {
    'op_state': op_state.all_assigns() if op_state else {},
    'inputs': user_input,
    TELEM_EVENT_TYPE_KEY: OP_STEP_EVENT_TYPE
  }


def action2config(action: Action) -> Dict:
  if isinstance(action, MultiAction):
    return action.serialize()
  elif isinstance(action, Action):
    return {
      mc.KIND_KEY: MultiAction.__name__,
      mc.TITLE_KEY: action.get_title(),
      mc.INFO_KEY: action.get_info(),
      SUB_ACTIONS_KEY: [
        action.serialize()
      ]
    }
  else:
    lwar(f"DANGER action is not an Action {type(action)}: {action}")


def sanitize_commit_bundle(overrides: Dict, defaults: Dict) -> Dict:
  output = {}
  for key, default in defaults.items():
    override = (overrides or {}).get(key)
    if override == {}:
      final_dict = {}
    elif override is None:
      final_dict = default
    else:
      final_dict = override
    output[key] = utils.flat2deep(final_dict)

  for mandatory_type in consts.TARGET_TYPES:
    if mandatory_type not in output.keys():
      output[mandatory_type] = {}

  return output


def filter_inputs_by_type(fields: List[Field], inputs: Dict, _type: str):
  flat_inputs = utils.deep2flat(inputs)

  def find_field(_id):
    return next(filter(lambda f: f.get_id() == _id, fields), None)

  gate = lambda k: find_field(k) and find_field(k).get_bucket_type() == _type
  filtered_flat = {k: v for (k, v) in flat_inputs.items() if gate(k)}
  return utils.flat2deep(filtered_flat)


ACTION_KEY = 'action'
NEXT_STEP_KEY = 'next'
FIELDS_KEY = 'fields'
SUMMARY_DESCRIPTOR = 'summary_desc'
COMMIT_KEY = 'commit'
DEFAULT_COMMIT_KEY = 'default_commit'

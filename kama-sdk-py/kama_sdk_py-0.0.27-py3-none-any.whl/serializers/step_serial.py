from typing import Dict

from kama_sdk.core.core.config_man import config_man
from kama_sdk.model.operation.field import Field
from kama_sdk.model.input import input_serializer
from kama_sdk.model.operation.operation_state import OperationState
from kama_sdk.model.operation.step import Step


def ser_embedded_field(field: Field) -> Dict:
  variable = field.get_variable()
  value = variable.current_or_default_value()
  input_model = variable.get_input_model()

  return dict(
    id=field.get_id(),
    title=field.get_title(),
    info=field.get_info(),
    is_inline=field.is_inline_chart_var(),
    default=value,
    **input_serializer.in_variable(input_model),
  )


def ser_refreshed(step: Step, values: Dict, state: OperationState) -> Dict:
  """
  Standard serializer for a step.
  :param step: Step class instance.
  :param values: current user input
  :param state: current operation state
  :return: serialized Step in dict form.
  """
  parent = step.get_parent()
  parent_id = parent.get_id() if parent else None
  config_man.get_user_vars()
  visible_fields = step.filter_visible_fields(values, state)
  summary_desc = step.get_summary_descriptor(values, state)
  return dict(
    id=step.get_id(),
    title=step.get_title(),
    synopsis=step.get_synopsis(),
    info=step.get_info(),
    flags=[],
    stage_id=parent_id,
    summary_desc=summary_desc,
    fields=list(map(ser_embedded_field, visible_fields))
  )

from kama_sdk.model.operation.operation import Operation
from kama_sdk.model.operation.step import Step
from kama_sdk.serializers.common_serializers import ser_meta


def ser_standard(operation: Operation):
  """
  Standard serializer for an Operation.
  :param operation: Operation instance.
  :return: serialized Operation dict.
  """
  return dict(
    **ser_meta(operation),
    tags=operation.get_tags(),
    synopsis=operation.get_synopsis(),
    step_metas=list(map(ser_step_meta, operation.get_steps())),
    space=operation.get_space_id()
  )


def ser_step_meta(step: Step):
  """
  Standard serializer for a Step.
  :param step: Stage instance.
  :return: serialized Stage dict.
  """
  return ser_meta(step)


def ser_full(operation: Operation):
  """
  Full serializer for an Operation - includes the Operation itself as well as
  related Stages and Prerequisites.
  :param operation: Operation instance.
  :return: serialized Operation dict.
  """
  return ser_standard(operation)

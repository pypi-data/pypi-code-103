from typing import Optional

from k8kat.res.base.kat_res import KatRes

from kama_sdk.core.core.types import ErrorCapture
from kama_sdk.model.action.base.action import Action, ActionError
from kama_sdk.model.base.common import RESOURCE_SELECTOR_KEY, KAT_RES_KEY
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.k8s.resource_selector import ResourceSelector
from kama_sdk.utils import utils


class DeleteResourceAction(Action):
  """
  Deletes a single resource, which can be passed explicitly, or
  queried dynamically with a `ResourceSelector`.
  """

  def get_title(self) -> str:
    if kat_res := self.get_kat_res():
      return f"Delete {kat_res.kind}/{kat_res.name}"
    else:
      return "Victim resource does not exist"

  def get_info(self) -> str:
    verb = "" if self.should_wait_until_gone else "do not"
    return f"Delete the resource, {verb} wait until it is destroyed"

  def should_raise_on_not_found(self) -> bool:
    raw = self.get_local_attr(TREAT_MISSING_AS_FATAL_KEY)
    return utils.any2bool(raw)

  def should_wait_until_gone(self) -> bool:
    value = self.get_attr(WAIT_TIL_GONE_KEY, backup=True)
    return utils.any2bool(value)

  def get_selector(self) -> ResourceSelector:
    return self.inflate_child(ResourceSelector, attr=RESOURCE_SELECTOR_KEY)

  @model_attr(cached=True)
  def get_kat_res(self) -> Optional[KatRes]:
    """
    If an explict `kat_res: KatRes` attribute is passed, return it. Otherwise,
    return the query result for the `resource_selector: ResourceSelector`.
    :return:
    """
    if explicit := self.get_attr(KAT_RES_KEY):
      return explicit
    else:
      query_results = self.get_selector().query_cluster()
      return next(iter(query_results), None)

  def perform(self) -> None:
    """
    If the `kat_res: KatRes` is defined, request for Kubernetes to
    delete it via `k8kat`, waiting until deletion depending on the
    `wait_until_gone: bool` attribute.

    If the victim is not present, raise an `ActionError` where the
    fatality is given by the `not_found_is_fatal: bool` attribute.
    :return:
    """
    if victim_res := self.get_kat_res():
      victim_res.delete(wait_until_gone=self.should_wait_until_gone())
    else:
      raise ActionError(ErrorCapture(
        fatal=self.should_raise_on_not_found(),
        reason="Victim resource did not exist",
        type="delete_victim_not_found"
      ))


WAIT_TIL_GONE_KEY = 'wait_until_gone'
TREAT_MISSING_AS_FATAL_KEY = 'not_found_is_fatal'

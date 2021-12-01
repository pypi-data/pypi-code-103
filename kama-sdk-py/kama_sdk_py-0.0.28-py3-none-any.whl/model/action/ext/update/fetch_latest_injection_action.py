from typing import Optional, Dict
from kama_sdk.core.core import updates_man, hub_api_client
from kama_sdk.core.core.types import InjectionsDesc, ErrorCapture
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.action_errors import FatalActionError
from kama_sdk.model.base.mc import TITLE_KEY, INFO_KEY


class FetchLatestInjectionsAction(Action):

  def get_title(self) -> str:
    return self.get_local_attr(TITLE_KEY) or DEFAULT_TITLE

  def get_info(self) -> str:
    return self.get_local_attr(INFO_KEY) or DEFAULT_INFO

  def perform(self) -> Optional[Dict]:
    bundle: InjectionsDesc = updates_man.latest_injection_bundle()
    raise_on_bundle_na(bundle)
    return dict(injections=bundle)


def raise_on_bundle_na(injection_bundle: Optional[InjectionsDesc]):
  if not injection_bundle:
    host = hub_api_client.backend_host()
    raise FatalActionError(ErrorCapture(
      type='injection_fetch',
      reason=f"Negative response from NMachine API ({host})"
    ))


DEFAULT_TITLE = "Commit TAM with new version/type"
DEFAULT_INFO = "Patch the Kamafile entry for KTEA definition"

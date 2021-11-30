from typing import Optional

from kama_sdk.core.core import updates_man, hub_api_client
from kama_sdk.core.core.types import ReleaseDict, ErrorCapture
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.action_errors import FatalActionError
from kama_sdk.model.base.mc import INFO_KEY, TITLE_KEY


class FetchReleaseAction(Action):

  def get_title(self) -> str:
    return self.get_local_attr(TITLE_KEY) or DEFAULT_TITLE

  def get_info(self) -> str:
    return self.get_local_attr(INFO_KEY) or DEFAULT_INFO

  def get_release_id(self) -> str:
    return self.get_attr(RELEASE_ID_KEY)

  def perform(self) -> Optional[ReleaseDict]:
    space = self.get_space_id()
    release = updates_man.fetch_release(self.get_release_id(), space)
    self.raise_if_none(release)
    return dict(release=release)

  def raise_if_none(self, update: Optional[ReleaseDict]) -> None:
    if not update:
      host = hub_api_client.backend_host()
      release_id = self.get_release_id()
      raise FatalActionError(ErrorCapture(
        type='fetch_update',
        reason=f"fetch failed update id={release_id} host {host}",
        extras=dict(host=host, release_id=release_id)
      ))


KTEA_KEY = 'ktea'
RELEASE_ID_KEY = "release_id"
DEFAULT_TITLE = "Read update from upstream"
DEFAULT_INFO = "Read update from upstream"

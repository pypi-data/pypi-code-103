from kama_sdk.core.core import updates_man
from kama_sdk.core.core.types import ReleaseDict
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.base.mc import TITLE_KEY, INFO_KEY


class CommitKteaFromReleaseAction(Action):

  def get_title(self) -> str:
    return self.get_local_attr(TITLE_KEY) or DEFAULT_TITLE

  def get_info(self) -> str:
    return self.get_local_attr(INFO_KEY) or DEFAULT_INFO

  def get_release(self) -> ReleaseDict:
    return self.get_attr(RELEASE_DICT_KEY)

  def perform(self):
    release_dict = self.get_release()
    updates_man.commit_new_ktea(release_dict)


RELEASE_DICT_KEY = 'release'
DEFAULT_TITLE = "Commit TAM with new version/type"
DEFAULT_INFO = "Patch the Kamafile entry for TAM definition"

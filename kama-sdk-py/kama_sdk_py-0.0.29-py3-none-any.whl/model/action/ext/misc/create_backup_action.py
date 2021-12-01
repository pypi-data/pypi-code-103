from datetime import datetime
from typing import Optional

from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.core.types import ErrorCapture, KamafileBackup
from kama_sdk.core.telem import backups_manager
from kama_sdk.core.telem.backups_manager import TRIGGER_AUTO
from kama_sdk.core.telem.telem_manager import telem_manager
from kama_sdk.model.action.base.action import Action
from kama_sdk.model.action.base.action_errors import ActionError
from kama_sdk.model.base.mc import TITLE_KEY, INFO_KEY


class CreateBackupAction(Action):
  """
  Creates a backup via the `backups_manager` module. Failure triggers
  a non-fatal `ActionError`.
  """

  def get_title(self) -> Optional[str]:
    return self.get_local_attr(TITLE_KEY) or DEFAULT_TITLE

  def get_info(self) -> Optional[str]:
    return self.get_local_attr(INFO_KEY) or DEFAULT_INFO

  def perform(self) -> None:
    if telem_manager.is_enabled():
      try:
        config = config_man.read_spaces()
        backups_manager.create(KamafileBackup(
          trigger=TRIGGER_AUTO,
          data=config,
          timestamp=str(datetime.now())
        ))
      except Exception as e:
        raise ActionError(ErrorCapture(
          fatal=False,
          reason=str(e),
          type='backup_telem_failure'
        ))
    else:
      self.add_logs([
        "Telemetry plugin disabled/offline",
        "Skipping create backup"
      ])


DEFAULT_TITLE = "Backup kamafile to database"
DEFAULT_INFO = "Write kamafile to telemetry database"

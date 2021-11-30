import time

from werkzeug.utils import cached_property

from kama_sdk.model.action.base.action import Action


class WaitAction(Action):

  def get_title(self) -> str:
    return f"Wait {self.duration_seconds()} seconds"

  @cached_property
  def info(self) -> str:
    return f"Holds the thread for the requested duration"

  def duration_seconds(self) -> int:
    return int(self.get_attr('duration_seconds', 3))

  def perform(self) -> None:
    time.sleep(self.duration_seconds())

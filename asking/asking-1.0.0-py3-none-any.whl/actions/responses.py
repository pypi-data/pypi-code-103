from json import dumps

from ansiscape import bright_yellow

from asking.actions.action import Action, ActionResult
from asking.exceptions import NothingToDoError


class ResponsesAction(Action):
    def perform(self) -> ActionResult:
        try:
            _ = self._action["responses"]
        except KeyError:
            raise NothingToDoError()

        s = dumps(self.state.responses, indent=2, sort_keys=True)
        dumped = bright_yellow(s).encoded if self.state.color else s

        self.state.out.write(dumped)
        self.state.out.write("\n\n")

        return ActionResult(next=None)

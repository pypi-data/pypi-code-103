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

        dumped = dumps(self.state.responses, indent=2, sort_keys=True)

        self.state.out.write("\n")
        self.state.out.write(bright_yellow(dumped).encoded)
        self.state.out.write("\n")
        return ActionResult(next=None)

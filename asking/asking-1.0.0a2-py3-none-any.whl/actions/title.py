from ansiscape import double_underline, heavy

from asking.actions.action import Action, ActionResult
from asking.exceptions import NothingToDoError


class TitleAction(Action):
    def perform(self) -> ActionResult:
        try:
            title = self._action["title"]
        except KeyError:
            raise NothingToDoError()

        self.state.out.write("\n")
        self.state.out.write(double_underline(heavy(title)).encoded)
        self.state.out.write("\n")
        return ActionResult(next=None)

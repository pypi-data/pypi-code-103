from asking.actions.action import Action, ActionResult


class TextAction(Action):
    def perform(self) -> ActionResult:
        text = self.get_string("text")

        self.state.out.write(text)
        self.state.out.write("\n\n")
        return ActionResult(next=None)

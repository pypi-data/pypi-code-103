import re
from typing import Any, Dict, Iterable, List, Optional, Union

from ansiscape import bright_green, heavy, italic
from ansiscape.checks import should_emit_codes

from asking.actions.action import Action, ActionResult
from asking.exceptions import AskingError, NothingToDoError
from asking.prompts import get_prompt
from asking.protocols import AskActionProtocol, BranchProtocol, StateProtocol


class Branch(BranchProtocol):
    def __init__(self, branch: Dict[str, Any], state: StateProtocol) -> None:
        self._branch = branch
        self._state = state

    @property
    def response(self) -> List[str]:
        response: Union[None, Any, List[Any]] = self._branch.get("response", None)
        if response is None:
            raise AskingError("no response key")

        if isinstance(response, list):
            return ["" if r is None else str(r) for r in response]

        return ["" if response is None else str(response)]

    def is_regex(self, value: str) -> bool:
        return value.startswith("^") and value.endswith("$")

    def matches_response(self, value: str) -> bool:
        for response in self.response:
            if response == "" and response == value:
                return True

            if not response.startswith("^"):
                response = f"^{response}"

            if not response.endswith("$"):
                response = f"{response}$"

            if re.match(response, value):
                self._state.logger.debug('value "%s" matches "%s"', value, response)
                return True
            self._state.logger.debug('value "%s" does not match "%s"', value, response)

        return False

    def perform_actions(self) -> Optional[str]:
        actions: Union[None, Any, List[Dict[str, Any]]] = self._branch.get("then", None)
        if not isinstance(actions, list):
            raise AskingError("no then")
        return self._state.perform_actions(actions)


AnyDict = Dict[str, Any]


class AskAction(Action, AskActionProtocol):
    @property
    def ask(self) -> AnyDict:
        ask: Union[None, Any, AnyDict] = self._action.get("ask", None)
        if isinstance(ask, dict):
            return ask
        raise NothingToDoError()

    @property
    def key(self) -> Optional[str]:
        key: Optional[Any] = self.ask.get("key", None)
        return None if key is None else str(key)

    @property
    def recall(self) -> bool:
        return bool(self.ask.get("recall", False))

    @property
    def branches(self) -> Iterable[Branch]:
        branches: Union[None, Any, List[AnyDict]] = self.ask.get("branches", None)
        if not isinstance(branches, list):
            raise AskingError("no branches")

        for branch_dict in branches:
            yield Branch(branch=branch_dict, state=self.state)

    def perform(self) -> ActionResult:
        question = self.get_string("question", source=self.ask, wrap=False)

        prompt = get_prompt(self)

        if prompt:
            prompt = f" {prompt}"

        text = (
            bright_green(heavy(question), prompt).encoded
            if self.state.color
            else heavy(question).encoded + prompt
            if should_emit_codes()
            else question + prompt
        )

        self.state.out.write(text)
        self.state.out.write("\n")

        next: Optional[str] = None

        bp = ": "
        input_prompt = bright_green(bp).encoded if self.state.color else bp

        direction = self.state.get_direction(self.key) if self.key else None

        while next is None:
            if direction is None:
                # This isn't unit testable:
                response = input(input_prompt)  # pragma: no cover
            else:
                response = direction
                self.state.out.write(input_prompt)
                self.state.out.write(
                    italic(response).encoded if should_emit_codes() else response
                )
                self.state.out.write("\n")

            self.state.out.write("\n")

            if self.recall and self.key and not response:
                response = self.state.get_response(self.key) or ""

            for branch in self.branches:
                if branch.matches_response(response):
                    # This is unit testable only with a key, so getting coverage
                    # without a key is tricky.
                    if self.key:  # pragma: no cover
                        self.state.save_response(key=self.key, value=response)
                    next = branch.perform_actions()

        return ActionResult(next=next)

from typing import List, Type

from asking.actions.action import Action, ActionResult
from asking.actions.ask import AskAction
from asking.actions.goto import GotoAction
from asking.actions.responses import ResponsesAction
from asking.actions.stop import StopAction
from asking.actions.text import TextAction
from asking.actions.title import TitleAction

registered_actions: List[Type[Action]] = [
    TitleAction,
    TextAction,
    ResponsesAction,
    AskAction,
    GotoAction,
    StopAction,
]

"""In execution order."""

__all__ = [
    "ActionResult",
    "AskAction",
    "GotoAction",
    "ResponsesAction",
    "StopAction",
    "TextAction",
    "TitleAction",
]

from typing import Optional, Text

from bf_nlu.exceptions import bf_nluException


class bf_nluCoreException(bf_nluException):
    """Basic exception for errors raised by bf_nlu Core."""


class StoryParseError(bf_nluCoreException, ValueError):
    """Raised if there is an error while parsing a story file."""

    def __init__(self, message) -> None:
        self.message = message


class UnsupportedDialogueModelError(bf_nluCoreException):
    """Raised when a model is too old to be loaded.

    Attributes:
        message -- explanation of why the model is invalid
    """

    def __init__(self, message: Text, model_version: Optional[Text] = None) -> None:
        self.message = message
        self.model_version = model_version

    def __str__(self) -> Text:
        return self.message


class AgentNotReady(bf_nluCoreException):
    """Raised if someone tries to use an agent that is not ready.

    An agent might be created, e.g. without an interpreter attached. But
    if someone tries to parse a message with that agent, this exception
    will be thrown."""

    def __init__(self, message: Text) -> None:
        self.message = message

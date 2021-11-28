from typing import Any


class Stop(Exception):
    """
    Raised to stop script execution.

    Arguments:
        reason: Reason for stopping.
    """

    def __init__(self, reason: Any) -> None:
        self._reason = reason
        super().__init__(repr(reason))

    @property
    def reason(self) -> Any:
        """
        Reason for stopping.
        """

        return self._reason


class AskingError(Exception):
    pass


class NothingToDoError(AskingError):
    def __init__(self) -> None:
        super().__init__("nothing to do")


class StageError(AskingError):
    def __init__(self, key: str, msg: str) -> None:
        super().__init__(f'"{key}" stage: {msg}')


class StageNotFoundError(StageError):
    def __init__(self, key: str) -> None:
        super().__init__(key, "not found")

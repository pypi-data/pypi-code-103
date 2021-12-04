class ClineError(Exception):
    pass


class CannotMakeArguments(ClineError):
    pass


class UserNeedsHelp(ClineError):
    def __init__(self, explicit: bool) -> None:
        super().__init__("user needs help")
        self.explicit = explicit


class UserNeedsVersion(ClineError):
    def __init__(self) -> None:
        super().__init__("user needs version")

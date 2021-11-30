from datek_jaipur.errors import EventValidationError


class GameCreatedValidationError(EventValidationError):
    pass


class PlayerNamesAreSameError(GameCreatedValidationError):
    pass

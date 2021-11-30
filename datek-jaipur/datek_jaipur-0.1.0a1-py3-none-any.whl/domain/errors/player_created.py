from datek_jaipur.errors import EventValidationError


class PlayerCreatedValidationError(EventValidationError):
    pass


class InvalidNameError(PlayerCreatedValidationError):
    pass

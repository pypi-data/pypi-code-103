class JaipurError(Exception):
    pass


class EventValidationError(JaipurError):
    pass


class EventAlreadyAppliedError(JaipurError):
    pass


class EventNotAppliedError(JaipurError):
    pass


class ExactlyTwoPlayersRequiredError(JaipurError):
    pass
